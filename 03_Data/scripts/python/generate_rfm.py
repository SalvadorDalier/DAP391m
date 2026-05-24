import pandas as pd
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
clean_path = os.path.join(script_dir, '../../data/processed/02_Cleaned_Data_Filtered.csv')
rfm_path = os.path.join(script_dir, '../../data/processed/customer_rfm.csv')

print("Loading cleaned data...")
df = pd.read_csv(clean_path)

print("Calculating RFM metrics...")
# Ensure datetime format
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
# Reference date is 1 day after the latest invoice
ref_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

# Calculate RFM
rfm = df.groupby('Customer ID').agg({
    'InvoiceDate': lambda x: (ref_date - x.max()).days,
    'Invoice': 'nunique',
    'Price': lambda x: (x * df.loc[x.index, 'Quantity']).sum() # Calculate Monetary
}).reset_index()

rfm.rename(columns={
    'Customer ID': 'CustomerID',
    'InvoiceDate': 'Recency',
    'Invoice': 'Frequency',
    'Price': 'Monetary'
}, inplace=True)

# Remove any negative monetary (returns) for RFM score if necessary, but keep for now.
# Scores 1-5 (5 is best)
rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)

# Segment Logic based on rfm_logic_summary.md
def get_segment(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
    if r in [4, 5] and f in [4, 5] and m in [4, 5]:
        return 'Champions'
    elif f in [4, 5] and m in [4, 5] and r in [2, 3, 4]:
        return 'Loyal Customers'
    elif r in [4, 5] and f <= 2 and m <= 2:
        return 'New Customers'
    elif r in [1, 2] and f >= 3 and m >= 3:
        return 'At Risk'
    elif r in [1, 2] and f in [1, 2] and m in [1, 2]:
        return 'Lost'
    else:
        return 'Regular Customers'

rfm['Segment'] = rfm.apply(get_segment, axis=1)

# Add Mock Coupon data
# Assign random coupon types and discount values, and random IsRedeemed
np.random.seed(42)
coupon_types = ['PERCENTAGE', 'FIXED_AMOUNT', 'BOGO']
discount_values = [10, 20, 5, 15]

rfm['CouponType'] = np.random.choice(coupon_types, size=len(rfm))
rfm['DiscountValue'] = np.random.choice(discount_values, size=len(rfm))
rfm['IsRedeemed'] = np.random.choice([0, 1], size=len(rfm), p=[0.7, 0.3])

print("Saving RFM data...")
rfm.to_csv(rfm_path, index=False)
print("RFM data saved to:", rfm_path)
