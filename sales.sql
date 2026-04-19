-- =============================================
-- STEP 1: Create Database
-- =============================================
CREATE DATABASE IF NOT EXISTS sales_intelligence_hub;
USE sales_intelligence_hub;

-- =============================================
-- STEP 2: Create branches Table
-- =============================================
CREATE TABLE IF NOT EXISTS branches (
    branch_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_name VARCHAR(100) NOT NULL,
    branch_admin_name VARCHAR(100) NOT NULL
);

-- =============================================
-- STEP 3: Create customer_sales Table
-- =============================================
CREATE TABLE IF NOT EXISTS customer_sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_id INT NOT NULL,
    date DATE NOT NULL,
    name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(15) NOT NULL,
    product_name VARCHAR(30) NOT NULL,
    gross_sales DECIMAL(12,2) NOT NULL,
    received_amount DECIMAL(12,2) DEFAULT 0,
    pending_amount DECIMAL(12,2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status ENUM('Open', 'Close') DEFAULT 'Open',
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE CASCADE
);

-- =============================================
-- STEP 4: Create users Table
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    branch_id INT NULL,
    role ENUM('Super Admin', 'Admin') NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL
);

-- =============================================
-- STEP 5: Create payment_splits Table
-- =============================================
CREATE TABLE IF NOT EXISTS payment_splits (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id) ON DELETE CASCADE
);

-- =============================================
-- STEP 6: Create Trigger to Auto-Update received_amount
-- =============================================
DELIMITER //

CREATE TRIGGER update_received_amount
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE total_received DECIMAL(12,2);
    
    -- Calculate total amount paid for this sale
    SELECT SUM(amount_paid) INTO total_received
    FROM payment_splits
    WHERE sale_id = NEW.sale_id;
    
    -- Update the received_amount in customer_sales table
    UPDATE customer_sales
    SET received_amount = total_received,
        status = CASE 
            WHEN gross_sales - total_received <= 0 THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
END //

DELIMITER ;

-- =============================================
-- STEP 7: Insert Branch Data
-- =============================================
INSERT INTO branches (branch_id, branch_name, branch_admin_name) VALUES
(1, 'Chennai', 'Arun Kumar'),
(2, 'Bangalore', 'Ravi Shankar'),
(3, 'Hyderabad', 'Suresh Reddy'),
(4, 'Delhi', 'Neha Sharma'),
(5, 'Mumbai', 'Rahul Mehta'),
(6, 'Pune', 'Amit Patil'),
(7, 'Kolkata', 'Subham Ghosh'),
(8, 'Ahmedabad', 'Raj Patel');

-- =============================================
-- STEP 8: Insert Users Data
-- =============================================
INSERT INTO users (username, password, branch_id, role, email) VALUES
('superadmin', 'super123', NULL, 'Super Admin', 'superadmin@company.com'),
('admin_chennai', 'admin123', 1, 'Admin', 'chennai@company.com'),
('admin_bangalore', 'admin123', 2, 'Admin', 'bangalore@company.com'),
('admin_hyderabad', 'admin123', 3, 'Admin', 'hyderabad@company.com'),
('admin_delhi', 'admin123', 4, 'Admin', 'delhi@company.com'),
('admin_mumbai', 'admin123', 5, 'Admin', 'mumbai@company.com'),
('admin_pune', 'admin123', 6, 'Admin', 'pune@company.com'),
('admin_kolkata', 'admin123', 7, 'Admin', 'kolkata@company.com'),
('admin_ahmedabad', 'admin123', 8, 'Admin', 'ahmedabad@company.com');



SELECT user_id, username, role, branch_id, email FROM users;
SELECT username, role FROM users;
