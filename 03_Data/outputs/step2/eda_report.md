# Step 2: EDA Report — Coupon Redemption Prediction

## 1. Data Cleaning Summary
- Rows before cleaning: 1067372
- Rows after cleaning: 779425
- Missing CustomerID dropped: 243007 rows
- Outliers capped (p99): Quantity=144.00, Price=14.95

## 2. RFM Distribution
| Segment | Count | Avg Recency | Avg Frequency | Avg Monetary |
|---|---|---|---|---|
| At Risk | 1445 | 201.19 | 2.7 | 780.21 |
| Champions | 1303 | 25.86 | 17.9 | 8590.2 |
| Hibernating | 1458 | 374.47 | 1.31 | 317.65 |
| Lost | 321 | 572.86 | 1.0 | 135.35 |
| Loyal | 1351 | 95.59 | 5.56 | 1885.09 |


## 3. Redemption Rate Insights
- Overall redemption rate: 38.91%
- Highest redemption: Champions at 71.91%
- Lowest redemption: Lost at 10.90%
- CouponType with highest redemption: BOGO

## 4. Key EDA Observations
- Redeemed customers have lower Recency (mean: 117.04 vs 255.01 days)
- Redeemed customers purchase more frequently (mean: 9.82 vs 4.04 times)
- Higher DiscountValue does not correlate with redemption (correlation = 0.01)

## 5. Train/Test Split
- Temporal cutoff date: 2011-11-20
- Train set: 4703 rows (2009-12-01 → 2011-11-20)
- Test set:  1175 rows (2011-11-20 → 2011-12-09)
- Data leakage check: PASSED

## 6. Class Balance
- IsRedeemed=1: 38.91% | IsRedeemed=0: 61.09%
- SMOTE recommendation: No double check
