-- ============================================================
-- PROJECT 11: Business Analysis Queries
-- Database: Project11DB
-- Updated to match schema: fact_sales, customers, customer_rfm
-- ============================================================

USE Project11DB;
GO

-- 1. Tổng quan hiệu suất kinh doanh (Business Performance Overview)
SELECT 
    ROUND(SUM(quantity * unit_price), 2) AS Total_Revenue_GBP,
    COUNT(DISTINCT invoice_no) AS Total_Orders,
    COUNT(DISTINCT customer_hash) AS Total_Customers,
    SUM(quantity) AS Total_Items_Sold
FROM [dbo].[fact_sales];
GO

-- 2. Xu hướng doanh thu theo thời gian (Revenue Trends Over Time)
SELECT 
    FORMAT(invoice_date, 'yyyy-MM') AS [Month],
    ROUND(SUM(quantity * unit_price), 2) AS Monthly_Revenue
FROM [dbo].[fact_sales]
GROUP BY FORMAT(invoice_date, 'yyyy-MM')
ORDER BY [Month];
GO

-- 3. Phân tích phân khúc khách hàng (Customer Segment Analysis)
-- Dựa trên bảng rfm đã tính toán
SELECT 
    rfm_segment,
    COUNT(customer_hash) AS Total_Customers,
    AVG(recency) AS Avg_Recency,
    AVG(frequency) AS Avg_Frequency,
    SUM(monetary) AS Total_Revenue_Segment
FROM [dbo].[customers] c
JOIN [dbo].[customer_rfm] r ON c.customer_hash = r.customer_hash
GROUP BY rfm_segment
ORDER BY Total_Revenue_Segment DESC;
GO

-- 4. Tỷ lệ đổi mã giảm giá (Coupon Redemption Rate)
SELECT 
    cc.campaign_name,
    cc.target_segment,
    COUNT(cr.redemption_id) AS Redemptions,
    cc.budget_gbp
FROM [dbo].[coupon_campaigns] cc
LEFT JOIN [dbo].[coupon_redemptions] cr ON cc.campaign_id = cr.campaign_id
GROUP BY cc.campaign_id, cc.campaign_name, cc.target_segment, cc.budget_gbp;
GO
