--Gợi ý khuyến mãi cho khách hàng, tạo function (admin)
--Trả về danh sách khuyến mãi khách có thể áp dụng theo loại phòng, số ngày ở và ngày bắt đầu đặt
CREATE OR REPLACE FUNCTION suggest_promotions(
    p_room_type VARCHAR,
    p_stay_days INT,
    p_current_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    promotion_id INT,
    promotion_name VARCHAR,
    discount_percentage NUMERIC,
    start_date DATE,
    end_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.promotion_id, 
        p.promotion_name, 
        p.discount_percentage, 
        p.start_date, 
        p.end_date
    FROM promotion p
    WHERE p_current_date BETWEEN p.start_date AND p.end_date
      AND (p.applicable_room_types IS NULL OR p.applicable_room_types = '' OR p.applicable_room_types = p_room_type)
      AND p.minimum_stay_days <= p_stay_days;
END;
$$ LANGUAGE plpgsql;
SELECT * FROM suggest_promotions('Double', 3, '2025-06-20');



--Thống kê tổng tiền dịch vụ theo các loại trong mùa du lịch (tạo function)
CREATE OR REPLACE FUNCTION services_revenue_by_type_summer_2025()
RETURNS TABLE (
    service_type CHAR(100),
    total_revenue NUMERIC(10,2),
    number_of_services BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.service_type,                         
        SUM(s.price)::NUMERIC(10,2) AS total_revenue,
        COUNT(*) AS number_of_services
    FROM service s
    JOIN booking b ON s.booking_id = b.booking_id
    WHERE EXTRACT(YEAR FROM b.check_out_date) = 2025
      AND EXTRACT(MONTH FROM b.check_out_date) BETWEEN 6 AND 8
    GROUP BY s.service_type
    ORDER BY total_revenue DESC;
END;
$$ LANGUAGE plpgsql;
SELECT * FROM services_revenue_by_type_summer_2025();


--Thống kê top 5 khách hàng có lượng chi tiêu nhiều nhất năm 
CREATE OR REPLACE FUNCTION top_spending_customers(year_input INT)
RETURNS TABLE (
    customer_id INT,
    full_name VARCHAR(100),
    total_spent NUMERIC(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.customer_id, 
        c.full_name, 
        SUM(i.final_amount)::NUMERIC(10,2)
    FROM customer c
    JOIN booking b ON c.customer_id = b.customer_id
    JOIN invoice i ON b.booking_id = i.booking_id
    WHERE EXTRACT(YEAR FROM i.issue_date) = year_input
      AND i.payment_status = 1
    GROUP BY c.customer_id, c.full_name
    ORDER BY SUM(i.final_amount) DESC
    LIMIT 5;
END;
$$ LANGUAGE plpgsql;
SELECT * FROM top_spending_customers(2025);


--Gợi ý phòng trống theo yêu cầu của khách hàng
CREATE OR REPLACE FUNCTION suggest_available_rooms(
    p_room_type VARCHAR,
    p_min_capacity INT,
    p_check_in_date DATE,
    p_check_out_date DATE
)
RETURNS TABLE (
    room_id INT,
    room_number INT,
    capacity INT,
    price_per_night NUMERIC(10,2),
    floor_number INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.room_id,
        r.room_number,
        r.capacity,
        r.price_per_night,
        r.floor_number
    FROM room r
    WHERE r.room_type = p_room_type
      AND r.capacity >= p_min_capacity
      AND r.status != 2  
      AND NOT EXISTS (
            SELECT 1 FROM booking b
            WHERE b.room_id = r.room_id
              AND b.status = 1
              AND (
                   b.check_in_date < p_check_out_date
               AND b.check_out_date > p_check_in_date
              )
      )
    ORDER BY r.price_per_night;
END;
$$ LANGUAGE plpgsql;
SELECT * FROM suggest_available_rooms('Deluxe', 3, '2025-06-10', '2025-06-13');




--Truy vấn phân tích tỉ lệ sử dụng dịch vụ của khách hàng trong khoảng thời gian
SELECT 
    TO_CHAR(b.check_out_date, 'YYYY-MM') AS month,
    s.service_type,
    COUNT(*) AS usage_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY TO_CHAR(b.check_out_date, 'YYYY-MM')), 2) AS percentage
FROM service s
JOIN booking b ON s.booking_id = b.booking_id
WHERE EXTRACT(YEAR FROM b.check_out_date) = 2025
  AND EXTRACT(MONTH FROM b.check_out_date) BETWEEN 5 AND 8
GROUP BY month, s.service_type
ORDER BY month, percentage DESC;



