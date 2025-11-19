
-- PRODUCT REPORTS
CREATE OR REPLACE VIEW monthlyOrderTotals AS
SELECT YEAR(o.orderDate) AS year, MONTH(o.orderDate) AS month, ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS totalSales
FROM orders o
JOIN orderdetails od ON o.orderNumber = od.orderNumber
GROUP BY year, month
ORDER BY year, month;

CREATE OR REPLACE VIEW orderLineTotals AS
SELECT YEAR(o.orderDate) AS year, p.productLine, ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS totalSales
FROM orders o
JOIN orderdetails od ON o.orderNumber = od.orderNumber
JOIN products p ON od.productCode = p.productCode
GROUP BY year, p.productLine
ORDER BY year, p.productLine;

CREATE OR REPLACE VIEW productOrderTotals AS
SELECT YEAR(o.orderDate) AS year, p.productName, ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS totalSales
FROM orders o
JOIN orderdetails od ON o.orderNumber = od.orderNumber
JOIN products p ON od.productCode = p.productCode
GROUP BY year, p.productName
ORDER BY year, totalSales DESC;


-- CUSTOMER REPORTS
CREATE OR REPLACE VIEW customerOrderTotals AS
SELECT YEAR(o.orderDate) AS year, c.customerName, ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS totalOrders
FROM customers c
LEFT JOIN orders o ON c.customerNumber = o.customerNumber
LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber
GROUP BY year, c.customerName
ORDER BY year, totalOrders DESC;

CREATE OR REPLACE VIEW customerPaymentTotals AS
SELECT YEAR(p.paymentDate) AS year, c.customerName, ROUND(SUM(p.amount), 2) AS totalPayments
FROM customers c
LEFT JOIN payments p ON c.customerNumber = p.customerNumber
GROUP BY year, c.customerName
ORDER BY year, totalPayments DESC;


-- EMPLOYEE REPORTS
CREATE OR REPLACE VIEW employeeOrderTotals AS
SELECT YEAR(o.orderDate) AS year, CONCAT(e.firstName, ' ', e.lastName) AS fullName, ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS totalOrders
FROM employees e
LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
LEFT JOIN orders o ON c.customerNumber = o.customerNumber
LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber
GROUP BY year, fullName
ORDER BY year, totalOrders DESC;

CREATE OR REPLACE VIEW employeeOrderNumbers AS
SELECT YEAR(o.orderDate) AS year, CONCAT(e.firstName, ' ', e.lastName) AS fullName, COUNT(DISTINCT o.orderNumber) AS numOrders
FROM employees e
LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
LEFT JOIN orders o ON c.customerNumber = o.customerNumber
GROUP BY year, fullName
ORDER BY year, numOrders DESC;

