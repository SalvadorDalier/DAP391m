# Summary of RFM Segmentation Logic

RFM (Recency, Frequency, Monetary) analysis is a marketing technique used to quantitatively rank and group customers based on the recency, frequency and monetary total of their recent transactions.

## 1. Calculating RFM Metrics
- **Recency (R)**: The number of days since the customer's last purchase. Calculated as the difference between a reference date (usually the day after the most recent transaction in the dataset) and the customer's maximum `InvoiceDate`.
- **Frequency (F)**: The total number of unique transactions (`InvoiceNo`) made by the customer.
- **Monetary (M)**: The total monetary value of all purchases made by the customer. Calculated as the sum of (`Quantity` * `Price`).

## 2. Assigning RFM Scores (1-5)
Each customer is assigned a score from 1 to 5 for each RFM metric. We use quintiles (20% bins) to rank customers relative to the entire customer base.
- **R_Score**: 5 (purchased very recently) to 1 (hasn't purchased in a long time). Note: lower recency days get a higher score.
- **F_Score**: 5 (purchases very frequently) to 1 (purchases rarely).
- **M_Score**: 5 (spends a lot) to 1 (spends very little).

## 3. Defining Segments
Based on the combination of R, F, and M scores, we categorize customers into actionable segments. While custom thresholds can be defined, a common approach is as follows:

| Segment | Logic / Thresholds (Example) | Description |
| :--- | :--- | :--- |
| **Champions** | `R_Score` in [4, 5] AND `F_Score` in [4, 5] AND `M_Score` in [4, 5] | Bought recently, buy often, and spend the most. Best customers. |
| **Loyal Customers** | `F_Score` in [4, 5] AND `M_Score` in [4, 5] AND `R_Score` in [2, 3, 4] | Spend good money and often. Responsive to promotions. |
| **New Customers** | `R_Score` in [4, 5] AND `F_Score` <= 2 AND `M_Score` <= 2 | Bought most recently, but not often. Need to build relationship. |
| **At Risk** | `R_Score` in [1, 2] AND `F_Score` >= 3 AND `M_Score` >= 3 | Spent big money and purchased often, but haven't returned recently. Need to win them back. |
| **Lost** | `R_Score` in [1, 2] AND `F_Score` in [1, 2] AND `M_Score` in [1, 2] | Lowest recency, frequency, and monetary scores. Likely churned. |

*(Note: In the provided Python script, a simplified scoring and segmentation logic using combined string scores is implemented to classify these segments).*
