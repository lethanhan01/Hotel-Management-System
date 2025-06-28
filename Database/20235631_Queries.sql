--Đăng ký tài khoản khách hàng, kiểm tra trùng username / email/ CCCD(user)
ALTER TABLE customer
ALTER COLUMN customer_id ADD GENERATED ALWAYS AS IDENTITY;

SELECT setval(
  		pg_get_serial_sequence('customer', 'customer_id'),
  		(SELECT MAX(customer_id) FROM customer)
);

CREATE OR REPLACE FUNCTION register_customer(
    p_full_name VARCHAR,
    p_identification_number CHAR(12),
    p_phone_number CHAR(11),
    p_email VARCHAR,
    p_nationality VARCHAR,
    p_username VARCHAR,
    p_password VARCHAR
) RETURNS TEXT AS $$
DECLARE
    duplicate_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO duplicate_count
    FROM customer
    WHERE username = p_username OR email = p_email OR identification_number = p_identification_number;
    IF duplicate_count > 0 THEN
        RETURN 'Thong tin đang ky đa ton tai!';
    END IF;

    INSERT INTO customer (
        full_name, identification_number, phone_number, email, nationality, username, password, registration_date, account_status
    ) VALUES (
        p_full_name, p_identification_number, p_phone_number, p_email, p_nationality, p_username, p_password, CURRENT_DATE, 1
    );
    RETURN 'Dang ky thanh cong!';
END;
$$ LANGUAGE plpgsql;

SELECT register_customer(
    'Le Thanh An',
    '012345678901',
    '09876543210',
    'leva@example.com',
    'Vietnam',
    'levana01',
    'matkhau123'
);

SELECT register_customer(
   	 'Nguyễn Văn D',
  	  '222222222222',
   	 '09222222222',
   	 'vand@example.com',
    	 'Vietnam',
   	 'levana01',           -- Trùng username
    	 'matkhau789'
);

--Tổng hợp feedback/đánh giá sau khi đặt phòng theo đơn booking của khách hàng(admin)

CREATE OR REPLACE VIEW v_booking_review_summary AS
SELECT
    b.booking_id,
    c.customer_id,
    c.full_name AS customer_name,
    r.room_number,
    b.check_in_date,
    b.check_out_date,
    rv.review_id,
    rv.rating,
    rv.comment,
    rv.review_date,
    rv.response,
    rv.response_date
FROM booking b
JOIN customer c ON b.customer_id = c.customer_id
JOIN room r ON b.room_id = r.room_id
LEFT JOIN review rv ON b.booking_id = rv.booking_id
ORDER BY c.customer_id, b.booking_id;

SELECT * FROM v_booking_review_summary;



--Đưa ra danh sách vật tư mà khách sạn hiện đang có và số lượng theo thứ tự giảm dần 
SELECT item_id, item_name, quantity_in_stock
FROM inventory
ORDER BY quantity_in_stock DESC, item_name;

CREATE INDEX idx_inventory_quantity_itemname ON inventory(quantity_in_stock DESC, item_name);


--Đưa ra danh sách vật tư dưới 1 mốc số lượng nhất định-(admin)
SELECT item_id, item_name, quantity_in_stock
FROM inventory
WHERE quantity_in_stock < 10
ORDER BY quantity_in_stock ASC, item_name;


CREATE INDEX idx_inventory_quantityname_asc ON inventory(quantity_in_stock ASC, item_name);

EXPLAIN ANALYZE
SELECT item_id, item_name, quantity_in_stock
FROM inventory
WHERE quantity_in_stock < 10
ORDER BY quantity_in_stock ASC, item_name;


--Tạo view xem thông tin 10 ưu đãi mới nhất cho phòng đơn và phòng đôi(admin)

CREATE OR REPLACE VIEW v_top10_newest_single_double_promotions AS
SELECT *
FROM promotion
WHERE applicable_room_types IN ('Single', 'Double')
   OR applicable_room_types IS NULL
ORDER BY start_date DESC
LIMIT 10;
Select * from  v_top10_newest_single_double_promotions;

--Đưa ra các supplier cho item và số item họ cung cấp theo thứ tự giảm dần(admin)

SELECT supplier_info, COUNT(*) AS total_items
FROM inventory
GROUP BY supplier_info
ORDER BY total_items DESC, supplier_info;


CREATE INDEX idx_inventory_supplier ON inventory(supplier_info);

--View: Xem tổng hợp thông tin khách hàng (profile + số lần đặt phòng + tổng chi tiêu)
CREATE OR REPLACE VIEW v_customer_summary AS
SELECT 
    c.customer_id,
    c.full_name,
    c.phone_number,
    c.email,
    c.nationality,
    c.membership_level,
    COUNT(b.booking_id) AS total_bookings,
    COALESCE(SUM(i.final_amount), 0) AS total_spent
FROM customer c
LEFT JOIN booking b ON c.customer_id = b.customer_id
LEFT JOIN invoice i ON b.booking_id = i.booking_id AND i.payment_status = 1
GROUP BY c.customer_id;
	
SELECT * FROM v_customer_summary;

