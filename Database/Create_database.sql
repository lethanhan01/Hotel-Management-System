-- Truy vấn tạo bảng 
CREATE DATABASE hotel_management;

CREATE TABLE IF NOT EXISTS public.customer
(
    customer_id integer NOT NULL,
    full_name character varying(100) COLLATE pg_catalog."default",
    identification_number character(12) COLLATE pg_catalog."default",
    phone_number character(11) COLLATE pg_catalog."default",
    email character varying(100) COLLATE pg_catalog."default",
    nationality character varying(100) COLLATE pg_catalog."default",
    username character varying(100) COLLATE pg_catalog."default",
    password character varying(50) COLLATE pg_catalog."default",
    registration_date date,
    membership_level integer DEFAULT 0,
    account_status integer,
    CONSTRAINT customer_pkey PRIMARY KEY (customer_id)
);
CREATE TABLE IF NOT EXISTS public.inventory
(
    item_id integer NOT NULL,
    item_name character varying(500) COLLATE pg_catalog."default",
    quantity_in_stock integer,
    unit_price numeric(10,2),
    supplier_info character varying COLLATE pg_catalog."default",
    location_in_storage character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT inventory_pkey PRIMARY KEY (item_id)
);
CREATE TABLE IF NOT EXISTS public.promotion
(
    promotion_id integer NOT NULL,
    promotion_name character varying(100) COLLATE pg_catalog."default",
    description character varying(500) COLLATE pg_catalog."default",
    discount_percentage numeric,
    start_date date,
    end_date date,
    applicable_room_types character varying(20) COLLATE pg_catalog."default",
    minimum_stay_days integer,
    CONSTRAINT promotion_pkey PRIMARY KEY (promotion_id)
);
CREATE TABLE IF NOT EXISTS public.room
(
    room_id integer NOT NULL,
    room_number integer,
    room_type character varying(20) COLLATE pg_catalog."default",
    capacity integer,
    price_per_night numeric(10,2),
    view_description character(500) COLLATE pg_catalog."default",
    amenities character(500) COLLATE pg_catalog."default",
    status integer,
    floor_number integer,
    CONSTRAINT room_pkey PRIMARY KEY (room_id)
);
CREATE TABLE IF NOT EXISTS public.booking
(
    booking_id integer NOT NULL,
    customer_id integer,
    room_id integer,
    promotion_id integer,
    check_in_date date,
    check_out_date date,
    booking_date date,
    status integer,
    special_requests character varying(500) COLLATE pg_catalog."default",
    deposit_amount numeric(10,2),
    cancellation_reason character varying(500) COLLATE pg_catalog."default",
    cancellation_date date,
    CONSTRAINT booking_pkey PRIMARY KEY (booking_id),
    CONSTRAINT booking_customer_id_fkey FOREIGN KEY (customer_id)
        REFERENCES public.customer (customer_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT booking_promotion_id_fkey FOREIGN KEY (promotion_id)
        REFERENCES public.promotion (promotion_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT booking_room_id_fkey FOREIGN KEY (room_id)
        REFERENCES public.room (room_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);
CREATE TABLE IF NOT EXISTS public.invoice
(
    invoice_id integer NOT NULL,
    booking_id integer,
    issue_date date,
    total_amount numeric(10,2),
    payment_method character(20) COLLATE pg_catalog."default",
    payment_status integer,
    tax_amount numeric(10,2),
    service_charges numeric(10,2),
    discount_amount numeric(10,2),
    final_amount numeric(10,2),
    CONSTRAINT invoice_pkey PRIMARY KEY (invoice_id),
    CONSTRAINT invoice_booking_id_fkey FOREIGN KEY (booking_id)
        REFERENCES public.booking (booking_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);
CREATE TABLE IF NOT EXISTS public.review
(
    review_id integer NOT NULL,
    booking_id integer,
    rating integer,
    comment character varying(500) COLLATE pg_catalog."default",
    review_date date,
    response character varying(500) COLLATE pg_catalog."default",
    response_date date,
    CONSTRAINT review_pkey PRIMARY KEY (review_id),
    CONSTRAINT review_booking_id_fkey FOREIGN KEY (booking_id)
        REFERENCES public.booking (booking_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);
CREATE TABLE IF NOT EXISTS public.room_inventory
(
    room_id integer NOT NULL,
    item_id integer NOT NULL,
    CONSTRAINT room_inventory_pkey PRIMARY KEY (room_id, item_id)
);
CREATE TABLE IF NOT EXISTS public.service
(
    service_id integer NOT NULL,
    service_name character varying(100) COLLATE pg_catalog."default",
    description character(500) COLLATE pg_catalog."default",
    booking_id integer,
    price numeric(10,2),
    service_type character(100) COLLATE pg_catalog."default",
    CONSTRAINT service_pkey PRIMARY KEY (service_id),
    CONSTRAINT booking_booking_id_fkey FOREIGN KEY (booking_id)
        REFERENCES public.booking (booking_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

-- Tạo sequence cho các khóa chính của 1 số bảng
CREATE OR REPLACE FUNCTION enable_identity_columns()
RETURNS void AS $$
DECLARE
    max_booking_id INTEGER;
    max_invoice_id INTEGER;
    max_customer_id INTEGER;
    max_service_id INTEGER;

BEGIN
    SELECT COALESCE(MAX(booking_id), 0) INTO max_booking_id FROM booking;
    SELECT COALESCE(MAX(invoice_id), 0) INTO max_invoice_id FROM invoice;
    SELECT COALESCE(MAX(customer_id), 0) INTO max_customer_id FROM customer;
    SELECT COALESCE(MAX(service_id), 0) INTO max_service_id FROM service;


    EXECUTE '
        ALTER TABLE booking
        ALTER COLUMN booking_id DROP DEFAULT,
        ALTER COLUMN booking_id ADD GENERATED ALWAYS AS IDENTITY (START WITH ' || (max_booking_id + 1) || ' INCREMENT BY 1)
    ';

    EXECUTE '
        ALTER TABLE invoice
        ALTER COLUMN invoice_id DROP DEFAULT,
        ALTER COLUMN invoice_id ADD GENERATED ALWAYS AS IDENTITY (START WITH ' || (max_invoice_id + 1) || ' INCREMENT BY 1)
    ';
    
    EXECUTE '
        ALTER TABLE customer
        ALTER COLUMN customer_id DROP DEFAULT,
        ALTER COLUMN customer_id ADD GENERATED ALWAYS AS IDENTITY (START WITH ' || (max_customer_id + 1) || ' INCREMENT BY 1)
    ';

    EXECUTE '
        ALTER TABLE service
        ALTER COLUMN service_id DROP DEFAULT,
        ALTER COLUMN service_id ADD GENERATED ALWAYS AS IDENTITY (START WITH ' || (max_service_id + 1) || ' INCREMENT BY 1)
    ';
END;
$$ LANGUAGE plpgsql;


-- Trigger tự động tính các trường giá tiền trong invoice 
CREATE OR REPLACE FUNCTION create_booking_with_invoice_fixed(
    p_customer_id INTEGER,
    p_room_id INTEGER,
    p_check_in_date DATE,
    p_check_out_date DATE,
    p_special_requests VARCHAR(500) DEFAULT NULL,
    p_deposit_amount NUMERIC(10,2) DEFAULT 0,
    p_promotion_code VARCHAR(100) DEFAULT NULL
)
RETURNS TABLE(
    booking_id INTEGER,
    invoice_id INTEGER,
    final_amount NUMERIC(10,2),
    message VARCHAR(500)
) AS $$
DECLARE
    v_booking_id INTEGER;
    v_invoice_id INTEGER;
    v_promotion_id INTEGER;
    v_final_amount NUMERIC(10,2);
    v_nights INTEGER;
    v_message VARCHAR(500) := 'Booking created successfully';
BEGIN
    -- Kiểm tra khách hàng
    IF NOT EXISTS (
        SELECT 1 FROM customer_profile 
        WHERE customer_id = p_customer_id AND account_status = 1
    ) THEN
        RETURN QUERY SELECT NULL, NULL, 0, 'Khach hang khong ton tai hoac khong hoat dong';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM room 
        WHERE room_id = p_room_id AND status = 0
    ) THEN
        RETURN QUERY SELECT NULL, NULL, 0, 'Phong khong ton tai hoac khong trong hoac dang bao tri';
        RETURN;
    END IF;

    IF EXISTS (
        SELECT 1 FROM booking 
        WHERE room_id = p_room_id 
        AND status IN (1)
        AND (
            (check_in_date <= p_check_in_date AND check_out_date > p_check_in_date) OR
            (check_in_date < p_check_out_date AND check_out_date >= p_check_out_date) OR
            (check_in_date >= p_check_in_date AND check_out_date <= p_check_out_date)
        )
    ) THEN
        RETURN QUERY SELECT NULL, NULL, 0, 'Phong da duoc dat';
        RETURN;
    END IF;

    IF p_check_in_date >= p_check_out_date OR p_check_in_date < CURRENT_DATE THEN
        RETURN QUERY SELECT NULL, NULL, 0, 'Ngay check_in, check_out khong hop le';
        RETURN;
    END IF;

    v_nights := p_check_out_date - p_check_in_date;

    v_promotion_id := NULL;
    IF p_promotion_code IS NOT NULL THEN
        SELECT pr.promotion_id
        INTO v_promotion_id
        FROM promotion pr
        JOIN room r ON r.room_id = p_room_id
        WHERE pr.promotion_name = p_promotion_code
        AND pr.start_date <= CURRENT_DATE
        AND pr.end_date >= CURRENT_DATE
        AND (pr.applicable_room_types IS NULL OR pr.applicable_room_types = '' OR POSITION(r.room_type IN pr.applicable_room_types) > 0)
        AND (pr.minimum_stay_days IS NULL OR pr.minimum_stay_days <= v_nights);

        IF FOUND THEN
            v_message := v_message || ' with promotion applied';
        ELSE
            v_message := v_message || ' (promotion not applicable)';
        END IF;
    END IF;

    INSERT INTO booking (
        customer_id, room_id, promotion_id, check_in_date, check_out_date, 
        booking_date, status, special_requests, deposit_amount
    ) VALUES (
        p_customer_id, p_room_id, v_promotion_id, p_check_in_date, p_check_out_date,
        CURRENT_DATE, 1, p_special_requests, p_deposit_amount
    ) RETURNING booking.booking_id INTO v_booking_id;

    UPDATE room
    SET status = 1
    WHERE room_id = p_room_id;

    INSERT INTO invoice (
        booking_id,
        issue_date,
        payment_method,
        payment_status
    ) VALUES (
        v_booking_id,
        CURRENT_DATE,
        'Cash',
        1
    ) RETURNING invoice.invoice_id INTO v_invoice_id;

    SELECT invoice.final_amount INTO v_final_amount 
    FROM invoice WHERE invoice.invoice_id = v_invoice_id;

    RETURN QUERY SELECT v_booking_id, v_invoice_id, v_final_amount, v_message;
END;
$$ LANGUAGE plpgsql;

-- function tự động tính tiền và thêm service vào booking
CREATE OR REPLACE FUNCTION add_service_to_booking(
    p_booking_id INTEGER,
    p_service_name VARCHAR(100),
    p_service_description VARCHAR(500),
    p_service_price NUMERIC(10,2),
    p_service_type VARCHAR(100) DEFAULT 'ADDITIONAL'
)
RETURNS TABLE(
    service_id INTEGER,
    updated_final_amount NUMERIC(10,2),
    message VARCHAR(500)
) AS $$
DECLARE
    v_service_id INTEGER;
    v_invoice_id INTEGER;
    v_updated_final_amount NUMERIC(10,2);
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM booking 
        WHERE booking.booking_id = p_booking_id 
        AND booking.status IN (1)
    ) THEN
        RETURN QUERY SELECT NULL::INTEGER, 0::NUMERIC(10,2), 'Booking not found or not active';
        RETURN;
    END IF;

    SELECT invoice.invoice_id 
    INTO v_invoice_id
    FROM invoice 
    WHERE invoice.booking_id = p_booking_id;

    IF v_invoice_id IS NULL THEN
        RETURN QUERY SELECT NULL::INTEGER, 0::NUMERIC(10,2), 'Invoice not found for this booking';
        RETURN;
    END IF;

    -- add service 
    INSERT INTO service (
        service_name, description, booking_id, price, service_type
    ) VALUES (
        p_service_name, p_service_description, p_booking_id, p_service_price, p_service_type
    ) RETURNING service.service_id INTO v_service_id;

    UPDATE invoice 
    SET issue_date = invoice.issue_date
    WHERE invoice.invoice_id = v_invoice_id;

    SELECT invoice.final_amount 
    INTO v_updated_final_amount
    FROM invoice 
    WHERE invoice.invoice_id = v_invoice_id;

    RETURN QUERY SELECT v_service_id, v_updated_final_amount, 'Service added successfully'::VARCHAR(500);
END;
$$ LANGUAGE plpgsql;

