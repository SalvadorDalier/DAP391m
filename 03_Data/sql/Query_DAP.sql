-- ============================================================
-- PROJECT 11: Business Analysis Queries
-- Database: Project11DB
-- Target Table: online_retail (Giả định từ Online Retail II dataset)
-- ============================================================

USE Project11DB;
GO

-- 1. Tổng quan hiệu suất kinh doanh (Business Performance Overview)
SELECT 
    ROUND(SUM(Quantity * UnitPrice), 2) AS Total_Revenue_GBP,
    COUNT(DISTINCT InvoiceNo) AS Total_Orders,
    COUNT(DISTINCT CustomerID) AS Total_Customers,
    SUM(Quantity) AS Total_Items_Sold
FROM online_retail;
GO

-- 2. Xu hướng doanh thu theo thời gian (Revenue Trends Over Time)
SELECT 
    FORMAT(InvoiceDate, 'yyyy-MM') AS [Month],
    ROUND(SUM(Quantity * UnitPrice), 2) AS Monthly_Revenue
FROM online_retail
GROUP BY FORMAT(InvoiceDate, 'yyyy-MM')
ORDER BY [Month];
GO

-- 3. Các sản phẩm mang lại giá trị cao nhất (Top Value Products)
SELECT TOP 10
    StockCode,
    Description,
    ROUND(SUM(Quantity * UnitPrice), 2) AS Total_Sales_Value
FROM online_retail
WHERE Description IS NOT NULL
GROUP BY StockCode, Description
ORDER BY Total_Sales_Value DESC;
GO

-- 4. Phân tích theo thị trường (Quốc gia) (Market Analysis - Country)
SELECT 
    Country,
    ROUND(SUM(Quantity * UnitPrice), 2) AS Revenue,
    COUNT(DISTINCT CustomerID) AS Customer_Count,
    COUNT(DISTINCT InvoiceNo) AS Order_Count
FROM online_retail
GROUP BY Country
ORDER BY Revenue DESC;
GO
