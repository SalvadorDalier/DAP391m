import pandas as pd
import os
import datetime

def save_excel_safe(df, filepath):
    # Excel max rows is 1048576, subtract 1 for header
    max_rows = 1048575
    if len(df) > max_rows:
        print(f"Warning: Data exceeds Excel row limit for {filepath}. Truncating to {max_rows} rows.")
        df.iloc[:max_rows].to_excel(filepath, index=False)
    else:
        df.to_excel(filepath, index=False)

def main():
    raw_path = './data/raw/online_retail_II.csv'
    out_dir = './data/processed/'
    os.makedirs(out_dir, exist_ok=True)
    
    print("Loading raw data...")
    df_raw = pd.read_csv(raw_path)
    
    # 1. Raw Data
    raw_csv = os.path.join(out_dir, 'project11_01_raw.csv')
    raw_xlsx = os.path.join(out_dir, 'project11_01_raw.xlsx')
    
    print("Saving Raw Data...")
    df_raw.to_csv(raw_csv, index=False)
    print("Saving Raw Data to Excel (this might take a few minutes)...")
    save_excel_safe(df_raw, raw_xlsx)
    
    # 2. Filtered Data
    print("Filtering data...")
    # Assume column names might be 'Customer ID' or 'CustomerID'
    cust_col = 'Customer ID' if 'Customer ID' in df_raw.columns else 'CustomerID'
    inv_col = 'Invoice' if 'Invoice' in df_raw.columns else 'InvoiceNo'
    
    df_filtered = df_raw.dropna(subset=[cust_col])
    df_filtered = df_filtered[~df_filtered[inv_col].astype(str).str.startswith('C')]
    df_filtered = df_filtered[(df_filtered['Quantity'] > 0) & (df_filtered['Price'] > 0)]
    
    filt_csv = os.path.join(out_dir, 'project11_02_filtered.csv')
    filt_xlsx = os.path.join(out_dir, 'project11_02_filtered.xlsx')
    
    print("Saving Filtered Data...")
    df_filtered.to_csv(filt_csv, index=False)
    print("Saving Filtered Data to Excel...")
    save_excel_safe(df_filtered, filt_xlsx)
    
    # 3. Final Data (RFM Features without Coupon Simulation)
    print("Generating Final RFM Features...")
    df_filtered['InvoiceDate'] = pd.to_datetime(df_filtered['InvoiceDate'])
    df_filtered['TotalSpend'] = df_filtered['Quantity'] * df_filtered['Price']
    
    reference_date = df_filtered['InvoiceDate'].max() + datetime.timedelta(days=1)
    
    rfm = df_filtered.groupby(cust_col).agg({
        'InvoiceDate': lambda x: (reference_date - x.max()).days,
        inv_col: 'nunique',
        'TotalSpend': 'sum'
    }).rename(columns={
        'InvoiceDate': 'Recency',
        inv_col: 'Frequency',
        'TotalSpend': 'Monetary'
    }).reset_index()
    
    # Assign Scores
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
    
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
            
    rfm['RFM_Segment'] = rfm.apply(assign_segment, axis=1)
    
    final_csv = os.path.join(out_dir, 'project11_03_final.csv')
    final_xlsx = os.path.join(out_dir, 'project11_03_final.xlsx')
    
    print("Saving Final Data...")
    rfm.to_csv(final_csv, index=False)
    save_excel_safe(rfm, final_xlsx)
    
    print("All datasets generated successfully!")

if __name__ == "__main__":
    main()
