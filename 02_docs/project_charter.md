# Project Charter: Coupon Redemption Prediction

## Business Problem Statement
Mass coupon campaigns waste marketing budget by targeting all customers indiscriminately. Sending discounts to customers who would have purchased anyway, or to customers who will never purchase regardless of the discount, leads to inefficient spending and reduced margins.

## Objectives & Success Metrics
**Objectives**:
- Build a predictive model to identify customers most likely to redeem coupons.
- Enable precise targeting for future marketing campaigns.
- Increase the overall return on investment (ROI) of marketing spend.

**Success Metrics**:
- **Conversion Rate (Redemption Rate)**: Increase the percentage of issued coupons that are actually redeemed.
- **Cost per Redemption**: Decrease the marketing cost required to drive a single redemption.
- **Incremental Revenue**: Increase the net revenue generated directly from the targeted coupon campaign compared to a control group.

## Target Variable & Feature Variables
- **Target Variable**: `IsRedeemed` (Binary: 0 for not redeemed, 1 for redeemed).
- **Feature Variables**: RFM scores (Recency, Frequency, Monetary), RFM segments, customer demographics (if available), past transaction history, coupon characteristics (Discount Value, Coupon Type), seasonality, etc.

## ROI Formula
ROI = (Incremental Revenue from Targeted Campaign - Cost of Campaign) / Cost of Campaign * 100

Where:
- **Incremental Revenue** = Revenue from customers who purchased due to the coupon - Revenue they would have generated without the coupon.
- **Cost of Campaign** = Sum of (Discount Value of Redeemed Coupons) + Operational/Distribution Costs.

## Timeline Estimate
- **Step 1: Data Collection & Preparation (Current)**: 1 week
- **Step 2: Exploratory Data Analysis (EDA) & Feature Engineering**: 1-2 weeks
- **Step 3: Model Development & Validation**: 2 weeks
- **Step 4: Deployment & A/B Testing**: 1-2 weeks
- **Total Estimated Timeline**: 5-7 weeks
