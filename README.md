# Hotel-Management-System
This repository contains the database project for a Hotel Management System, developed as part of the Database Practice course (IT3290) at Hanoi University of Science and Technology.

- **Instructor:** TS. Trần Văn Đặng
- **Team Members:**
    - Lê Văn Thành An (20236018)
    - Lê Thành An (20235631)
    - Trần Đức Nam Anh (20235655)
- **Project Completion:** June 2025

## About The Project

The project aims to address the complex operational demands of a modern hotel, where managing bookings, customer information, services, promotions, and revenue requires a robust and efficient system. The goal is to design and build a comprehensive database system that can handle large volumes of data, optimize operational workflows, and enhance the customer experience.

The system is built on **PostgreSQL** and leverages advanced database principles to ensure data consistency, integrity, and high-performance querying.

## Key Features

The system is designed with distinct functionalities for both customers and hotel administrators.

### Customer Functionality

* **Account Management:** Customers can create and manage their personal accounts.
* **Online Booking:** Search for available rooms, view details (price, amenities), and book rooms online.
* **Promotions & Discounts:** Apply valid promotion codes during the booking process.
* **Booking Management:** Cancel bookings online and view a complete history of transactions and booking statuses.
* **Service Requests:** Request additional services such as food, spa, or laundry during their stay.
* **Feedback & Reviews:** Leave reviews and ratings for rooms and services after their stay.

### Admin & Management Functionality

* **Revenue Management:** Track and generate statistics on revenue by day, week, month, or year. The system can also compare revenue across different room types and services.
* **Customer & Booking Management:** Access customer information, confirm bookings, and update room statuses (e.g., check-in, check-out, cancelled).
* **Room & Service Management:** Manage the details of rooms, services, amenities, and promotional programs.
* **Inventory Control:** Monitor the stock levels of hotel supplies (e.g., towels, kettles, TVs), manage supplier information, and receive alerts for low-stock items.
* **Financial Oversight:** Generate lists of customers with unpaid invoices and monitor overdue payments.
* **Performance Analytics:** Analyze customer feedback, track service usage popularity, and identify top-spending customers.

## Database Design

The database was designed following a structured analysis of the system's business requirements.

* **Key Entities:** The core of the system is built around the following entities:
    * `Customer`: Stores customer profiles, contact details, and membership information.
    * `Room`: Contains details for each hotel room, including type, capacity, price, and status.
    * `Booking`: Records all booking transactions, linking customers, rooms, and promotions.
    * `Invoice`: Manages financial records for each booking, including charges, taxes, and payment status.
    * `Service`: Details additional services offered by the hotel (e.g., spa, laundry).
    * `Promotion`: Stores information on all promotional campaigns and their conditions.
    * `Review`: Captures customer feedback and ratings tied to specific bookings.
    * `Inventory`: Tracks all physical items and supplies within the hotel.
* **Normalization:** The database schema is normalized to the **Third Normal Form (3NF)** to minimize data redundancy and ensure data integrity.
* **Diagrams:** The detailed **Entity-Relationship Diagram (ERD)** and **Relational Schema** can be found in the project report file: `Report/Báo cáo.pdf`.

## Technologies Used

* **Database:** PostgreSQL
* **Diagramming Tool:** draw.io

## Performance Optimization

To ensure the system runs efficiently, several performance tuning techniques were implemented:

* **Query Analysis:** The `EXPLAIN ANALYZE` tool in PostgreSQL was used to inspect query execution plans and identify performance bottlenecks.
* **Indexing:** Strategic indexes were created on frequently queried columns to accelerate data retrieval. For example, indexes were added to the `invoice` table (`idx_invoice_status_date`, `idx_invoice_booking_id`) and the `booking` table (`idx_booking_customer_id`) to speed up searches for unpaid bills.
* **Optimized Queries:** Complex queries, such as those for generating revenue reports, were structured using Common Table Expressions (CTEs) to improve readability and performance by breaking down the logic into simpler, temporary result sets.
