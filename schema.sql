-- ============================================================
-- SmartCart MySQL Database Schema (smartcart_db)
-- ============================================================

CREATE DATABASE IF NOT EXISTS smartcart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smartcart_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'customer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
);

-- 2. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    user_id INT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NULL,
    age INT DEFAULT 30,
    gender VARCHAR(20) DEFAULT 'Other',
    city VARCHAR(100) DEFAULT 'Mumbai',
    state VARCHAR(100) DEFAULT 'Maharashtra',
    preferred_category VARCHAR(100) DEFAULT 'Electronics',
    average_order_value FLOAT DEFAULT 0.0,
    total_purchases INT DEFAULT 0,
    purchase_frequency FLOAT DEFAULT 0.0,
    average_rating_given FLOAT DEFAULT 0.0,
    last_purchase_date VARCHAR(50) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_cust_id (customer_id)
);

-- 3. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL
);

-- 4. Products Table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NULL,
    brand VARCHAR(100) NULL,
    description TEXT NULL,
    price FLOAT NOT NULL,
    discount FLOAT DEFAULT 0.0,
    final_price FLOAT NOT NULL,
    rating FLOAT DEFAULT 4.0,
    review_count INT DEFAULT 0,
    stock INT DEFAULT 50,
    popularity_score FLOAT DEFAULT 50.0,
    tags TEXT NULL,
    age_group VARCHAR(50) DEFAULT 'All Ages',
    gender_target VARCHAR(50) DEFAULT 'All',
    color VARCHAR(50) DEFAULT 'Standard',
    size VARCHAR(50) DEFAULT 'Standard',
    image_url VARCHAR(500) NULL,
    status VARCHAR(20) DEFAULT 'Active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_prod_cat (category),
    INDEX idx_prod_id (product_id),
    INDEX idx_prod_name (name)
);

-- 5. Interactions Table
CREATE TABLE IF NOT EXISTS interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interaction_id VARCHAR(50) NOT NULL UNIQUE,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100) NULL,
    search_keyword VARCHAR(150) NULL,
    category VARCHAR(100) NULL,
    device VARCHAR(50) NULL,
    time_spent INT DEFAULT 30,
    product_viewed INT DEFAULT 0,
    added_to_wishlist INT DEFAULT 0,
    added_to_cart INT DEFAULT 0,
    purchased INT DEFAULT 0,
    rating_given INT DEFAULT 0,
    INDEX idx_int_cust (customer_id),
    INDEX idx_int_prod (product_id)
);

-- 6. Search History Table
CREATE TABLE IF NOT EXISTS search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    search_id VARCHAR(50) NULL,
    customer_id VARCHAR(50) NOT NULL,
    search_keyword VARCHAR(200) NOT NULL,
    search_category VARCHAR(100) NULL,
    search_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    result_clicked INT DEFAULT 0,
    product_clicked VARCHAR(200) NULL,
    INDEX idx_srch_cust (customer_id)
);

-- 7. Ratings Table
CREATE TABLE IF NOT EXISTS ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rating_id VARCHAR(50) NULL,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    rating INT NOT NULL,
    review_text TEXT NULL,
    rating_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_rat_prod (product_id),
    INDEX idx_rat_cust (customer_id)
);

-- 8. Wishlists Table
CREATE TABLE IF NOT EXISTS wishlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_wish_cust (customer_id)
);

-- 9. Cart Table
CREATE TABLE IF NOT EXISTS cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NULL,
    session_id VARCHAR(100) NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cart_cust (customer_id),
    INDEX idx_cart_sess (session_id)
);

-- 10. Cart Items Table
CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INT DEFAULT 1,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES cart(id) ON DELETE CASCADE
);

-- 11. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL UNIQUE,
    customer_id VARCHAR(50) NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount FLOAT NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'UPI',
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(250) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(20) NOT NULL,
    status VARCHAR(50) DEFAULT 'Placed',
    INDEX idx_order_id (order_id),
    INDEX idx_order_cust (customer_id)
);

-- 12. Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INT DEFAULT 1,
    unit_price FLOAT NOT NULL,
    discount FLOAT DEFAULT 0.0,
    total_price FLOAT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- 13. Recommendations Log Table
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NULL,
    product_id VARCHAR(50) NOT NULL,
    recommendation_type VARCHAR(50) DEFAULT 'Personalized',
    score FLOAT DEFAULT 0.0,
    shown_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    clicked INT DEFAULT 0,
    purchased INT DEFAULT 0,
    INDEX idx_rec_cust (customer_id),
    INDEX idx_rec_prod (product_id)
);

-- 14. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
