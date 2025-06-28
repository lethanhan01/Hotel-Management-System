-- Function hiện hóa đơn đặt phòng
CREATE OR REPLACE FUNCTION get_booking_details(p_booking_id INTEGER)
RETURNS TABLE(
    booking_id INTEGER,
    customer_name VARCHAR(100),
    room_number INTEGER,
    room_type VARCHAR(20),
    check_in_date DATE,
    check_out_date DATE,
    nights INTEGER,
    room_price NUMERIC(10,2),
    promotion_name VARCHAR(100),
    total_room_amount NUMERIC(10,2),
    service_charges NUMERIC(10,2),
    tax_amount NUMERIC(10,2),
    discount_amount NUMERIC(10,2),
    final_amount NUMERIC(10,2),
    payment_status INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.booking_id,
        c.full_name,
        r.room_number,
        r.room_type,
        b.check_in_date,
        b.check_out_date,
        (b.check_out_date - b.check_in_date)::INTEGER AS nights,
        r.price_per_night,
        p.promotion_name,
        COALESCE(i.total_amount, 0)::NUMERIC(10,2),
        COALESCE(i.service_charges, 0)::NUMERIC(10,2),
        COALESCE(i.tax_amount, 0)::NUMERIC(10,2),
        COALESCE(i.discount_amount, 0)::NUMERIC(10,2),
        COALESCE(i.final_amount, 0)::NUMERIC(10,2),
        COALESCE(i.payment_status, 0)::INTEGER
    FROM booking b
    JOIN customer c ON b.customer_id = c.customer_id
    JOIN room r ON b.room_id = r.room_id
    LEFT JOIN promotion p ON b.promotion_id = p.promotion_id
    LEFT JOIN invoice i ON b.booking_id = i.booking_id
    WHERE b.booking_id = p_booking_id;
END;
$$ LANGUAGE plpgsql;


-- Function cho khách hàng hủy phòng
CREATE OR REPLACE FUNCTION cancel_booking_by_customer(
    p_booking_id INTEGER,
    p_customer_id INTEGER,
    p_cancellation_reason VARCHAR(500)
)
RETURNS TABLE (
    booking_id INTEGER,
    message TEXT
) AS $$
DECLARE
    v_room_id INTEGER;
BEGIN
    -- Kiểm tra booking tồn tại, đúng khách và đang hoạt động
    SELECT b.room_id
    INTO v_room_id
    FROM booking b
    WHERE b.booking_id = p_booking_id
      AND b.customer_id = p_customer_id
      AND b.status IN (1);

    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL, 'Booking khong ton tai hoac khong thuoc ve khach hang nay';
        RETURN;
    END IF;

    UPDATE booking b
    SET status = 0,
        cancellation_reason = p_cancellation_reason,
        cancellation_date = CURRENT_DATE
    WHERE b.booking_id = p_booking_id;

    UPDATE room r
    SET status = 0
    WHERE r.room_id = v_room_id;

    RETURN QUERY SELECT p_booking_id, 'Booking da duoc huy';
END;
$$ LANGUAGE plpgsql;

-- View hiển thị thông tin của khách hàng
CREATE OR REPLACE VIEW customer_profile AS
SELECT 
    customer_id,
    full_name,
    identification_number,
    phone_number,
    email,
    nationality,
    username,
    registration_date,
    membership_level,
    CASE 
        WHEN account_status = 1 THEN 'Hoat dong'
        WHEN account_status = 0 THEN 'Tam khoa'
    END as account_status_text,
    CASE 
        WHEN membership_level = 0 THEN 'Thanh vien thuong'
        WHEN membership_level = 1 THEN 'Thanh vien bac'
        WHEN membership_level = 2 THEN 'Thanh vien vang'
    END as membership_level_text,
    CURRENT_DATE - registration_date as days_since_registration
FROM customer
WHERE account_status IN (0, 1);


-- Hiển thị xếp hạng khách hàng theo chi tiêu 
SELECT 
    c.customer_id,
    c.full_name,
    c.membership_level,
    COUNT(b.booking_id) as total_bookings,
    SUM(i.final_amount) as total_spent,
    COUNT(CASE 
		WHEN i.payment_status = 1 
		THEN 1 
	END) as paid_invoices,
    COUNT(CASE 
		WHEN i.payment_status = 0 
		THEN 1 
	END) as unpaid_invoices
FROM customer_profile c
LEFT JOIN booking b ON c.customer_id = b.customer_id
LEFT JOIN invoice i ON b.booking_id = i.booking_id
GROUP BY c.customer_id, c.full_name, c.membership_level
HAVING COUNT(b.booking_id) > 0  
ORDER BY total_spent DESC NULLS LAST;


-- Doanh thu theo tháng và loại phòng trong năm 2025
WITH invoice_with_date AS (
    SELECT 
        i.invoice_id,
        i.booking_id,
        i.final_amount,
        EXTRACT(YEAR FROM i.issue_date) AS year,
        EXTRACT(MONTH FROM i.issue_date) AS month
    FROM invoice i
    WHERE i.payment_status = 1
)
SELECT 
    iwd.year,
    iwd.month,
    r.room_type,
    SUM(iwd.final_amount) AS total_revenue
FROM invoice_with_date iwd
JOIN booking b ON iwd.booking_id = b.booking_id
JOIN room r ON b.room_id = r.room_id
GROUP BY iwd.year, iwd.month, r.room_type
ORDER BY iwd.year DESC, iwd.month DESC, total_revenue DESC;


-- Danh sách khách hàng chưa thanh toán
SELECT 
    i.invoice_id,
    c.full_name,
    i.issue_date,
    i.final_amount,
    i.payment_method,
    CURRENT_DATE - i.issue_date AS days_overdue
FROM invoice i
JOIN booking b ON i.booking_id = b.booking_id
JOIN customer_profile c ON b.customer_id = c.customer_id
WHERE i.payment_status = 0 AND CURRENT_DATE > i.issue_date
ORDER BY i.issue_date ASC;

CREATE INDEX idx_invoice_status_date ON invoice (payment_status, issue_date);
CREATE INDEX idx_invoice_booking_id ON invoice (booking_id);
CREATE INDEX idx_booking_customer_id ON booking (customer_id);


-- Khách hàng update thông tin cá nhân
CREATE OR REPLACE FUNCTION update_customer_profile(
    p_customer_id INTEGER,
    p_full_name VARCHAR(100) DEFAULT NULL,
    p_phone_number CHAR(11) DEFAULT NULL,
    p_email VARCHAR(100) DEFAULT NULL,
    p_nationality VARCHAR(100) DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    record_count INTEGER;
BEGIN
    -- Kiểm tra customer có tồn tại và đang hoạt động
    SELECT COUNT(*) INTO record_count 
    FROM customer 
    WHERE customer_id = p_customer_id AND account_status >= 0;
    
    IF record_count = 0 THEN
        RETURN FALSE;
    END IF;
    
    UPDATE customer 
    SET 
        full_name = COALESCE(p_full_name, full_name),
        phone_number = COALESCE(p_phone_number, pho	ne_number),
        email = COALESCE(p_email, email),
        nationality = COALESCE(p_nationality, nationality)
    WHERE customer_id = p_customer_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


