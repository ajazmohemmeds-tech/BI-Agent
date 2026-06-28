-- Database Setup for Business Intelligence Project (AdventureWorks dataset)

DROP TABLE IF EXISTS sales_order_items;
DROP TABLE IF EXISTS sales_orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS territories;

CREATE TABLE territories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    country_group VARCHAR(100) NOT NULL
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    segment VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50) NOT NULL,
    list_price DECIMAL(10, 2) NOT NULL,
    standard_cost DECIMAL(10, 2) NOT NULL
);

CREATE TABLE sales_orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    territory INTEGER REFERENCES territories(id)
);

CREATE TABLE sales_order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES sales_orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(15, 2) NOT NULL
);

INSERT INTO territories (id, name, region, country_group) VALUES
(1, 'Northwest', 'North America', 'North America'),
(2, 'Northeast', 'North America', 'North America'),
(3, 'Central', 'North America', 'North America'),
(4, 'Southwest', 'North America', 'North America'),
(5, 'Southeast', 'North America', 'North America'),
(6, 'Canada', 'North America', 'North America'),
(7, 'France', 'Europe', 'Europe'),
(8, 'Germany', 'Europe', 'Europe'),
(9, 'Australia', 'Pacific', 'Pacific'),
(10, 'United Kingdom', 'Europe', 'Europe'),
(11, 'Spain', 'Europe', 'Europe'),
(12, 'Italy', 'Europe', 'Europe'),
(13, 'Japan', 'Pacific', 'Pacific'),
(14, 'China', 'Pacific', 'Pacific'),
(15, 'India', 'Pacific', 'Pacific'),
(16, 'Brazil', 'South America', 'South America'),
(17, 'Argentina', 'South America', 'South America'),
(18, 'Mexico', 'North America', 'North America'),
(19, 'South Africa', 'Africa', 'Africa'),
(20, 'Nigeria', 'Africa', 'Africa');

INSERT INTO customers (id, first_name, last_name, email, country, city, segment) VALUES
(1, 'James', 'Smith', 'james.smith1@gmail.com', 'United States', 'United States City 3', 'Consumer'),
(2, 'Robert', 'Gonzalez', 'robert.gonzalez2@gmail.com', 'Australia', 'Australia City 5', 'Corporate'),
(3, 'Robert', 'Miller', 'robert.miller3@gmail.com', 'Italy', 'Italy City 2', 'Corporate'),
(4, 'Linda', 'Hernandez', 'linda.hernandez4@gmail.com', 'Australia', 'Australia City 5', 'Home Office'),
(5, 'Sarah', 'Smith', 'sarah.smith5@gmail.com', 'Australia', 'Australia City 4', 'Home Office'),
(6, 'David', 'Martinez', 'david.martinez6@gmail.com', 'Nigeria', 'Nigeria City 1', 'Home Office'),
(7, 'James', 'Hernandez', 'james.hernandez7@gmail.com', 'Brazil', 'Brazil City 2', 'Home Office'),
(8, 'Patricia', 'Martin', 'patricia.martin8@gmail.com', 'United States', 'United States City 5', 'Home Office'),
(9, 'Barbara', 'Moore', 'barbara.moore9@gmail.com', 'Italy', 'Italy City 2', 'Consumer'),
(10, 'Karen', 'Hernandez', 'karen.hernandez10@gmail.com', 'China', 'China City 3', 'Consumer'),
(11, 'Joseph', 'Garcia', 'joseph.garcia11@gmail.com', 'China', 'China City 2', 'Consumer'),
(12, 'Richard', 'Jones', 'richard.jones12@gmail.com', 'France', 'France City 3', 'Consumer'),
(13, 'Michael', 'Taylor', 'michael.taylor13@gmail.com', 'Japan', 'Japan City 5', 'Consumer'),
(14, 'William', 'Moore', 'william.moore14@gmail.com', 'United States', 'United States City 3', 'Consumer'),
(15, 'Joseph', 'Gonzalez', 'joseph.gonzalez15@gmail.com', 'United States', 'United States City 1', 'Home Office'),
(16, 'Jessica', 'Martinez', 'jessica.martinez16@gmail.com', 'Spain', 'Spain City 3', 'Consumer'),
(17, 'Susan', 'Rodriguez', 'susan.rodriguez17@gmail.com', 'Australia', 'Australia City 1', 'Corporate'),
(18, 'Jessica', 'Lopez', 'jessica.lopez18@gmail.com', 'France', 'France City 3', 'Home Office'),
(19, 'Thomas', 'Moore', 'thomas.moore19@gmail.com', 'United States', 'United States City 1', 'Home Office'),
(20, 'Elizabeth', 'Williams', 'elizabeth.williams20@gmail.com', 'Australia', 'Australia City 1', 'Consumer'),
(21, 'Joseph', 'Lopez', 'joseph.lopez21@gmail.com', 'Germany', 'Germany City 2', 'Consumer'),
(22, 'Joseph', 'Lopez', 'joseph.lopez22@gmail.com', 'Italy', 'Italy City 1', 'Corporate'),
(23, 'James', 'Hernandez', 'james.hernandez23@gmail.com', 'Spain', 'Spain City 5', 'Home Office'),
(24, 'Charles', 'Lopez', 'charles.lopez24@gmail.com', 'Germany', 'Germany City 3', 'Consumer'),
(25, 'Charles', 'Moore', 'charles.moore25@gmail.com', 'United Kingdom', 'United Kingdom City 5', 'Consumer'),
(26, 'Michael', 'Lopez', 'michael.lopez26@gmail.com', 'United States', 'United States City 1', 'Consumer'),
(27, 'Barbara', 'Wilson', 'barbara.wilson27@gmail.com', 'United States', 'United States City 1', 'Corporate'),
(28, 'Patricia', 'Garcia', 'patricia.garcia28@gmail.com', 'United States', 'United States City 4', 'Consumer'),
(29, 'Sarah', 'Martin', 'sarah.martin29@gmail.com', 'United States', 'United States City 3', 'Corporate'),
(30, 'Michael', 'Jones', 'michael.jones30@gmail.com', 'United States', 'United States City 4', 'Corporate');

INSERT INTO products (id, name, category, subcategory, list_price, standard_cost) VALUES
(1, 'Caps Model 207', 'Clothing', 'Caps', 291.31, 170.98),
(2, 'Road Bikes Model 244', 'Bikes', 'Road Bikes', 368.45, 240.88),
(3, 'Brakes Model 797', 'Components', 'Brakes', 467.12, 238.09),
(4, 'Caps Model 894', 'Clothing', 'Caps', 502.45, 348.64),
(5, 'Brakes Model 427', 'Components', 'Brakes', 252.87, 155.51),
(6, 'Caps Model 226', 'Clothing', 'Caps', 782.01, 453.94),
(7, 'Bottom Brackets Model 179', 'Components', 'Bottom Brackets', 724.95, 423.8),
(8, 'Touring Bikes Model 532', 'Bikes', 'Touring Bikes', 771.1, 412.17),
(9, 'Mountain Bikes Model 397', 'Bikes', 'Mountain Bikes', 598.75, 303.27),
(10, 'Mountain Bikes Model 421', 'Bikes', 'Mountain Bikes', 137.21, 112.65),
(11, 'Mountain Bikes Model 517', 'Bikes', 'Mountain Bikes', 19.18, 13.08),
(12, 'Touring Bikes Model 286', 'Bikes', 'Touring Bikes', 692.56, 388.15),
(13, 'Handlebars Model 912', 'Components', 'Handlebars', 750.45, 455.57),
(14, 'Chains Model 198', 'Components', 'Chains', 911.87, 463.15),
(15, 'Chains Model 124', 'Components', 'Chains', 151.86, 99.01),
(16, 'Gloves Model 596', 'Clothing', 'Gloves', 446.37, 352.16),
(17, 'Mountain Bikes Model 477', 'Bikes', 'Mountain Bikes', 431.83, 313.09),
(18, 'Chains Model 226', 'Components', 'Chains', 349.69, 272.61),
(19, 'Bib-Shorts Model 393', 'Clothing', 'Bib-Shorts', 757.36, 400.94),
(20, 'Caps Model 755', 'Clothing', 'Caps', 560.43, 287.24),
(21, 'Jerseys Model 455', 'Clothing', 'Jerseys', 76.98, 41.94),
(22, 'Caps Model 728', 'Clothing', 'Caps', 730.17, 485.42),
(23, 'Road Bikes Model 200', 'Bikes', 'Road Bikes', 617.17, 315.15),
(24, 'Bib-Shorts Model 905', 'Clothing', 'Bib-Shorts', 14.06, 10.99),
(25, 'Brakes Model 558', 'Components', 'Brakes', 160.12, 104.86),
(26, 'Caps Model 384', 'Clothing', 'Caps', 515.23, 305.28),
(27, 'Touring Bikes Model 569', 'Bikes', 'Touring Bikes', 307.94, 187.11),
(28, 'Mountain Bikes Model 683', 'Bikes', 'Mountain Bikes', 308.26, 160.21),
(29, 'Bottles and Cages Model 682', 'Accessories', 'Bottles and Cages', 759.38, 444.72),
(30, 'Touring Bikes Model 538', 'Bikes', 'Touring Bikes', 525.94, 320.19);

INSERT INTO sales_orders (id, customer_id, order_date, status, total_amount, territory) VALUES
(1, 15, '2024-06-11', 'Delivered', 5901.45, 8),
(2, 5, '2024-11-08', 'Shipped', 252.87, 17),
(3, 10, '2023-07-08', 'Delivered', 5745.8, 16),
(4, 23, '2023-11-17', 'Cancelled', 3749.07, 5),
(5, 24, '2024-07-11', 'Delivered', 345.9, 15),
(6, 23, '2023-02-25', 'Pending', 4514.51, 5),
(7, 22, '2024-11-25', 'Delivered', 2138.59, 15),
(8, 28, '2023-06-03', 'Shipped', 1234.34, 4),
(9, 8, '2023-12-11', 'Shipped', 2313.3, 13),
(10, 5, '2024-07-13', 'Pending', 611.64, 4),
(11, 14, '2023-06-06', 'Cancelled', 3182.63, 10),
(12, 26, '2023-09-03', 'Delivered', 2802.15, 14),
(13, 28, '2023-05-12', 'Processing', 873.93, 4),
(14, 19, '2024-10-08', 'Processing', 10459.73, 10),
(15, 13, '2024-04-22', 'Cancelled', 3091.6, 10),
(16, 15, '2023-12-04', 'Processing', 2910.23, 13),
(17, 9, '2024-03-19', 'Cancelled', 3397.89, 20),
(18, 9, '2023-06-24', 'Processing', 4015.2, 20),
(19, 19, '2024-07-29', 'Delivered', 303.72, 12),
(20, 16, '2023-07-20', 'Pending', 3647.48, 12),
(21, 20, '2024-11-14', 'Delivered', 2981.52, 17),
(22, 5, '2023-10-26', 'Shipped', 2512.25, 17),
(23, 1, '2023-05-18', 'Shipped', 2174.85, 5),
(24, 4, '2024-04-07', 'Pending', 7501.46, 13),
(25, 2, '2024-05-22', 'Delivered', 1000.82, 5),
(26, 22, '2024-04-15', 'Pending', 1004.9, 12),
(27, 4, '2024-01-27', 'Cancelled', 6379.96, 16),
(28, 15, '2023-06-27', 'Delivered', 924.78, 14),
(29, 28, '2024-07-24', 'Processing', 502.45, 8),
(30, 4, '2024-06-19', 'Shipped', 308.26, 17);

INSERT INTO sales_order_items (id, order_id, product_id, quantity, unit_price, line_total) VALUES
(1, 1, 12, 5, 692.56, 3462.8),
(2, 1, 19, 1, 757.36, 757.36),
(3, 1, 20, 3, 560.43, 1681.29),
(4, 2, 5, 1, 252.87, 252.87),
(5, 3, 3, 4, 467.12, 1868.48),
(6, 3, 6, 2, 782.01, 1564.02),
(7, 3, 8, 3, 771.1, 2313.3),
(8, 4, 4, 3, 502.45, 1507.35),
(9, 4, 20, 4, 560.43, 2241.72),
(10, 5, 24, 3, 14.06, 42.18),
(11, 5, 15, 2, 151.86, 303.72),
(12, 6, 22, 5, 730.17, 3650.85),
(13, 6, 17, 2, 431.83, 863.66),
(14, 7, 7, 2, 724.95, 1449.9),
(15, 7, 25, 2, 160.12, 320.24),
(16, 7, 2, 1, 368.45, 368.45),
(17, 8, 23, 2, 617.17, 1234.34),
(18, 9, 8, 3, 771.1, 2313.3),
(19, 10, 21, 4, 76.98, 307.92),
(20, 10, 15, 2, 151.86, 303.72),
(21, 11, 18, 3, 349.69, 1049.07),
(22, 11, 1, 1, 291.31, 291.31),
(23, 11, 2, 5, 368.45, 1842.25),
(24, 12, 20, 5, 560.43, 2802.15),
(25, 13, 1, 3, 291.31, 873.93),
(26, 14, 19, 5, 757.36, 3786.8),
(27, 14, 22, 4, 730.17, 2920.68),
(28, 14, 13, 5, 750.45, 3752.25),
(29, 15, 11, 5, 19.18, 95.9),
(30, 15, 7, 4, 724.95, 2899.8),
(31, 15, 11, 5, 19.18, 95.9),
(32, 16, 26, 1, 515.23, 515.23),
(33, 16, 9, 4, 598.75, 2395.0),
(34, 17, 19, 2, 757.36, 1514.72),
(35, 17, 2, 1, 368.45, 368.45),
(36, 17, 19, 2, 757.36, 1514.72),
(37, 18, 5, 3, 252.87, 758.61),
(38, 18, 9, 3, 598.75, 1796.25),
(39, 18, 22, 2, 730.17, 1460.34),
(40, 19, 15, 2, 151.86, 303.72),
(41, 20, 14, 4, 911.87, 3647.48),
(42, 21, 13, 3, 750.45, 2251.35),
(43, 21, 22, 1, 730.17, 730.17),
(44, 22, 4, 5, 502.45, 2512.25),
(45, 23, 7, 3, 724.95, 2174.85),
(46, 24, 19, 5, 757.36, 3786.8),
(47, 24, 8, 3, 771.1, 2313.3),
(48, 24, 3, 3, 467.12, 1401.36),
(49, 25, 28, 1, 308.26, 308.26),
(50, 25, 12, 1, 692.56, 692.56),
(51, 26, 4, 2, 502.45, 1004.9),
(52, 27, 19, 5, 757.36, 3786.8),
(53, 27, 14, 1, 911.87, 911.87),
(54, 27, 20, 3, 560.43, 1681.29),
(55, 28, 28, 3, 308.26, 924.78),
(56, 29, 4, 1, 502.45, 502.45),
(57, 30, 28, 1, 308.26, 308.26);

SELECT setval('territories_id_seq', (SELECT MAX(id) FROM territories));
SELECT setval('customers_id_seq', (SELECT MAX(id) FROM customers));
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
SELECT setval('sales_orders_id_seq', (SELECT MAX(id) FROM sales_orders));
SELECT setval('sales_order_items_id_seq', (SELECT MAX(id) FROM sales_order_items));

-- Create Read-Only User for AI Queries
CREATE USER bi_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE bi_db TO bi_readonly;
GRANT USAGE ON SCHEMA public TO bi_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bi_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bi_readonly;
