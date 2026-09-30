-- AgentRAG Database Initialization Script
-- Creates the sample employee and department tables with 25 realistic records.

CREATE DATABASE IF NOT EXISTS agentrag_db;
USE agentrag_db;

-- 1. Departments Table
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Employees Table
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    designation VARCHAR(100) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    joining_date DATE NOT NULL,
    CONSTRAINT fk_department
        FOREIGN KEY (department_id) 
        REFERENCES departments(department_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Seed Departments (5 Departments)
INSERT INTO departments (department_id, department_name) VALUES
(1, 'Engineering'),
(2, 'Human Resources'),
(3, 'Finance'),
(4, 'Product Management'),
(5, 'Sales');

-- 4. Seed Employees (25 Sample Records)
INSERT INTO employees (name, department_id, designation, salary, joining_date) VALUES
-- Engineering
('Alice Johnson', 1, 'Senior Software Engineer', 125000.00, '2022-03-15'),
('Bob Smith', 1, 'Backend Developer', 95000.00, '2023-06-01'),
('Charlie Davis', 1, 'DevOps Engineer', 110000.00, '2021-11-20'),
('Diana Miller', 1, 'Frontend Developer', 88000.00, '2024-01-10'),
('Ethan Wilson', 1, 'AI/ML Engineer', 135000.00, '2025-02-15'),
('Fiona Clark', 1, 'Software Engineer', 92000.00, '2025-04-01'),
('George Martin', 1, 'QA Automation Engineer', 82000.00, '2023-09-12'),
('Hannah White', 1, 'Engineering Manager', 155000.00, '2021-01-08'),

-- Human Resources
('Ian Moore', 2, 'HR Director', 120000.00, '2020-08-14'),
('Julia Taylor', 2, 'Talent Acquisition Specialist', 70000.00, '2023-02-18'),
('Kevin Anderson', 2, 'HR Generalist', 65000.00, '2024-07-01'),
('Laura Thomas', 2, 'People Operations Lead', 85000.00, '2022-10-11'),

-- Finance
('Michael Jackson', 3, 'Chief Financial Officer', 175000.00, '2019-05-01'),
('Nora Harris', 3, 'Senior Financial Analyst', 98000.00, '2022-04-19'),
('Oliver Lewis', 3, 'Accountant', 72000.00, '2023-11-05'),
('Penelope Young', 3, 'Payroll Specialist', 68000.00, '2025-01-20'),

-- Product Management
('Quinn Hall', 4, 'VP of Product', 165000.00, '2020-03-10'),
('Rachel Allen', 4, 'Senior Product Manager', 130000.00, '2022-09-01'),
('Samuel King', 4, 'Product Designer', 90000.00, '2023-04-15'),
('Tina Scott', 4, 'Associate Product Manager', 78000.00, '2025-03-01'),

-- Sales
('Uma Green', 5, 'Sales Director', 140000.00, '2021-06-15'),
('Victor Baker', 5, 'Enterprise Account Executive', 105000.00, '2022-12-01'),
('Wendy Adams', 5, 'Business Development Rep', 62000.00, '2024-05-10'),
('Xavier Nelson', 5, 'Customer Success Manager', 80000.00, '2023-08-22'),
('Yvonne Carter', 5, 'Sales Operations Analyst', 75000.00, '2025-05-18');
