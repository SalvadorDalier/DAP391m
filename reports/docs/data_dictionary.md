# Data Dictionary

## Online Retail II Dataset

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **InvoiceNo** | Nominal (String) | A 6-digit integral number uniquely assigned to each transaction. If this code starts with letter 'c', it indicates a cancellation. |
| **StockCode** | Nominal (String) | A 5-digit integral number uniquely assigned to each distinct product. |
| **Description** | Nominal (String) | Product (item) name. |
| **Quantity** | Numeric (Integer) | The quantities of each product (item) per transaction. |
| **InvoiceDate** | Datetime | Invoice Date and time. The day and time when each transaction was generated. |
| **Price** | Numeric (Float) | Unit price. Product price per unit in sterling (£). |
| **CustomerID** | Nominal (String) | A 5-digit integral number uniquely assigned to each customer. |
| **Country** | Nominal (String) | The name of the country where each customer resides. |

## Simulated Coupon Data

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **CustomerID** | Nominal (String) | Unique identifier for the customer (matches Online Retail II). |
| **CouponID** | Nominal (String) | Unique identifier for the issued coupon. |
| **DiscountValue** | Numeric (Float) | The monetary or percentage value of the discount offered. |
| **CouponType** | Nominal (String) | The type of coupon (e.g., `percentage`, `fixed`, `bogo`). |
| **IsRedeemed** | Binary (Integer) | The target variable indicating if the coupon was redeemed (1) or not (0). |
| **IssueDate** | Datetime | The date and time when the coupon was issued to the customer. |
| **RedeemDate** | Datetime | The date and time when the coupon was redeemed (Null if `IsRedeemed` is 0). |
