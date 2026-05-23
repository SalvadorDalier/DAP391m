-- Query 1: Redemption rate by coupon type
SELECT 
    CouponType,
    COUNT(CustomerID) AS TotalIssued,
    SUM(IsRedeemed) AS TotalRedeemed,
    CAST(SUM(IsRedeemed) AS FLOAT) / COUNT(CustomerID) AS RedemptionRate
FROM coupon_transactions
GROUP BY CouponType;

-- Query 2: Average discount value by customer segment
-- Assuming we have a 'customer_segments' table or view from the RFM analysis
-- If RFM_Segment is directly in coupon_transactions, we can omit the JOIN.
-- Here we assume RFM_Segment is stored in a separate table.
SELECT 
    s.RFM_Segment,
    AVG(c.DiscountValue) AS AvgDiscountValue
FROM coupon_transactions c
JOIN customer_segments s ON c.CustomerID = s.CustomerID
GROUP BY s.RFM_Segment;

-- Query 3: Count of customers who redeemed multiple coupons (frequency > 1)
SELECT 
    COUNT(CustomerID) AS MultiRedeemerCount
FROM (
    SELECT 
        CustomerID
    FROM coupon_transactions
    WHERE IsRedeemed = 1
    GROUP BY CustomerID
    HAVING COUNT(CouponID) > 1
) AS MultiRedeemers;
