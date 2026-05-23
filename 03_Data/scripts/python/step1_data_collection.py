import pandas as pd
import numpy as np
import os
import datetime

def main():
    print("--- Step 1: Data Collection & Preparation ---")
    
    # Define paths
    raw_data_dir = './data/raw/'
    
    # Identify the downloaded file (it might be .csv or .xlsx)
    files = []
    if os.path.exists(raw_data_dir):
        files = os.listdir(raw_data_dir)
        
    if not files:
        print(f"No files found in {raw_data_dir}. Please ensure the kaggle download command was successful.")
        return
        
    data_file = os.path.join(raw_data_dir, files[0])
    print(f"Reading dataset: {data_file}")
    
    try:
        if data_file.endswith('.csv'):
            df = pd.read_csv(data_file)
        elif data_file.endswith('.xlsx'):
            df = pd.read_excel(data_file)
        else:
            print("Unsupported file format.")
            return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Display dataset info
    print("\n--- Dataset Info ---")
    print(f"Shape: {df.shape}")
    print("\nColumn Names and Data Types:")
    print(df.dtypes)
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nNull Value Counts per Column:")
    print(df.isnull().sum())
    
    print("\n--- Calculating RFM Metrics ---")
    # Clean data (remove missing CustomerIDs and negative quantities/prices)
    df = df.dropna(subset=['Customer ID', 'CustomerID'], how='all') if 'Customer ID' in df.columns or 'CustomerID' in df.columns else df
    cust_col = 'Customer ID' if 'Customer ID' in df.columns else 'CustomerID'
    date_col = 'InvoiceDate'
    
    if cust_col not in df.columns or date_col not in df.columns:
        print("Required columns for RFM not found.")
        return
        
    df = df[df[cust_col].notnull()]
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    
    # Calculate Monetary value
    df['TotalSpend'] = df['Quantity'] * df['Price']
    
    # Ensure InvoiceDate is datetime
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Reference date for Recency (1 day after the max date in dataset)
    reference_date = df[date_col].max() + datetime.timedelta(days=1)
    
    # Group by CustomerID to calculate R, F, M
    rfm = df.groupby(cust_col).agg({
        date_col: lambda x: (reference_date - x.max()).days,
        'Invoice': 'nunique' if 'Invoice' in df.columns else 'InvoiceNo',
        'TotalSpend': 'sum'
    }).rename(columns={
        date_col: 'Recency',
        'Invoice': 'Frequency',
        'InvoiceNo': 'Frequency',
        'TotalSpend': 'Monetary'
    }).reset_index()
    
    print(rfm.head())
    
    print("\n--- Assigning RFM Scores and Segments ---")
    # Use qcut to assign 1-5 scores (5 is best)
    # Recency: lower is better, so labels are reversed
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    # Frequency: higher is better
    # Handle duplicate edges by using rank
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    # Monetary: higher is better
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
    
    # Concatenate scores
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    # Define Segments
    def assign_segment(row):
        r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 2 and f >= 4 and m >= 4:
            return 'Loyal'
        elif r >= 4 and f <= 2 and m <= 2:
            return 'New Customers'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2 and m <= 2:
            return 'Lost'
        else:
            return 'Regulars'
            
    rfm['Segment'] = rfm.apply(assign_segment, axis=1)
    print("\nSegment Value Counts:")
    print(rfm['Segment'].value_counts())
    
    print("\n--- Simulating Coupon Data ---")
    np.random.seed(42)
    customer_ids = rfm[cust_col].unique()
    num_coupons = len(customer_ids) * 2 # Issue 2 coupons per customer on average
    
    sampled_customers = np.random.choice(customer_ids, size=num_coupons)
    coupon_types = ['percentage', 'fixed', 'bogo']
    
    coupon_data = {
        'CustomerID': sampled_customers,
        'CouponID': [f'CUP_{i}' for i in range(num_coupons)],
        'DiscountValue': np.random.choice([10, 15, 20, 25, 50], size=num_coupons),
        'CouponType': np.random.choice(coupon_types, size=num_coupons),
        'IsRedeemed': np.random.choice([0, 1], size=num_coupons, p=[0.85, 0.15]),
        'IssueDate': [datetime.datetime.now() - datetime.timedelta(days=np.random.randint(1, 30)) for _ in range(num_coupons)]
    }
    
    coupon_df = pd.DataFrame(coupon_data)
    
    # Set RedeemDate
    def get_redeem_date(row):
        if row['IsRedeemed'] == 1:
            return row['IssueDate'] + datetime.timedelta(days=np.random.randint(1, 7))
        return pd.NaT
        
    coupon_df['RedeemDate'] = coupon_df.apply(get_redeem_date, axis=1)
    
    # Merge with RFM segments
    coupon_df = coupon_df.merge(rfm[[cust_col, 'Segment']], left_on='CustomerID', right_on=cust_col, how='left')
    coupon_df.rename(columns={'Segment': 'RFM_Segment'}, inplace=True)
    if cust_col != 'CustomerID':
        coupon_df.drop(columns=[cust_col], inplace=True)
        
    print(f"\nSimulated Coupon Table Shape: {coupon_df.shape}")
    print(coupon_df.head())
    
    # Save outputs
    os.makedirs('./data/processed/', exist_ok=True)
    rfm.to_csv('./data/processed/rfm_segments.csv', index=False)
    coupon_df.to_csv('./data/processed/coupon_transactions.csv', index=False)
    print("\nSaved RFM and Coupon data to ./data/processed/")

if __name__ == "__main__":
    main()
