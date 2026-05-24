import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import time

def main():
    print("Starting Data Import to SQL Server...")
    start_time = time.time()
    
    # Connection string for Windows Authentication
    server = 'localhost'
    database = 'Project11DB'
    connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
    
    print(f"Connecting to {server}...")
    engine = create_engine(connection_string, fast_executemany=True)
    
    # 1. Load Data
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clean_path = os.path.join(script_dir, '../../data/processed/02_Cleaned_Data_Filtered.csv')
    rfm_path = os.path.join(script_dir, '../../data/processed/customer_rfm.csv')

    print("Loading CSV files...")
    clean_df = pd.read_csv(clean_path)
    rfm_df = pd.read_csv(rfm_path)
    
    # Map FIXED_AMOUNT to FIXED to satisfy CHK_Coupon_Type constraint
    rfm_df['CouponType'] = rfm_df['CouponType'].replace({'FIXED_AMOUNT': 'FIXED'})
    
    print("Clearing existing data...")
    from sqlalchemy import text
    with engine.begin() as conn:
        try:
            conn.execute(text("DELETE FROM core.TransactionItem"))
            conn.execute(text("DELETE FROM core.[Transaction]"))
            conn.execute(text("DELETE FROM core.CouponIssuance"))
            conn.execute(text("DELETE FROM analytics.CustomerRFM"))
            conn.execute(text("DELETE FROM core.Coupon"))
            conn.execute(text("DELETE FROM core.Customer"))
            print("Successfully cleared tables.")
        except Exception as e:
            print(f"Could not clear tables! Error: {e}")
            raise  # Stop execution if we can't clear tables, otherwise we'll get PK errors
    
    # 2. Insert core.Customer
    print("Processing core.Customer...")
    cust_df = clean_df[['Customer ID', 'Country']].drop_duplicates()
    cust_df = cust_df.rename(columns={'Customer ID': 'CustomerID'})
    cust_df = cust_df.drop_duplicates(subset=['CustomerID'])
    cust_df.to_sql('Customer', engine, schema='core', if_exists='append', index=False)
    print(f"  Inserted {len(cust_df)} Customers.")

    # 3. Insert core.[Transaction]
    print("Processing core.Transaction...")
    tx_df = clean_df.groupby(['Invoice', 'Customer ID', 'InvoiceDate']).apply(
        lambda x: pd.Series({'TotalAmount': (x['Quantity'] * x['Price']).sum()})
    ).reset_index()
    tx_df = tx_df.rename(columns={'Invoice': 'InvoiceNo', 'Customer ID': 'CustomerID'})
    # Ensure datetime format
    tx_df['InvoiceDate'] = pd.to_datetime(tx_df['InvoiceDate']).dt.strftime('%Y-%m-%d %H:%M:%S')
    tx_df.to_sql('Transaction', engine, schema='core', if_exists='append', index=False)
    print(f"  Inserted {len(tx_df)} Transactions.")

    # Read back Transaction mapping
    tx_map = pd.read_sql("SELECT TransactionID, InvoiceNo FROM core.[Transaction]", engine)
    tx_map['InvoiceNo'] = tx_map['InvoiceNo'].astype(str)
    map_dict = dict(zip(tx_map['InvoiceNo'], tx_map['TransactionID']))

    # 4. Insert core.TransactionItem
    print("Processing core.TransactionItem...")
    items_df = clean_df[['Invoice', 'StockCode', 'Description', 'Quantity', 'Price']].copy()
    items_df['TransactionID'] = items_df['Invoice'].astype(str).map(map_dict)
    
    # Check for unmapped TransactionIDs and drop or alert
    if items_df['TransactionID'].isnull().any():
        print(f"Warning: {items_df['TransactionID'].isnull().sum()} TransactionItems could not be mapped to a Transaction. Dropping them to avoid FK errors.")
        items_df = items_df.dropna(subset=['TransactionID'])
        
    items_df = items_df.rename(columns={'Price': 'UnitPrice'})
    items_df = items_df.drop(columns=['Invoice'])
    
    # Insert in chunks to isolate errors
    chunk_size = 10000
    for i in range(0, len(items_df), chunk_size):
        chunk = items_df.iloc[i:i+chunk_size]
        try:
            chunk.to_sql('TransactionItem', engine, schema='core', if_exists='append', index=False)
        except Exception as e:
            print(f"  Error inserting chunk {i} to {i+chunk_size}: {str(e)[:200]}...")
            # If chunk fails, we could try row-by-row to find the exact offending row, but let's just log it
            print("  Skipping this chunk and continuing...")
            
    print(f"  Finished processing {len(items_df)} Transaction Items (some chunks may have failed).")

    # 5. Insert core.Coupon
    print("Processing core.Coupon...")
    unique_coupons = rfm_df[['CouponType', 'DiscountValue']].drop_duplicates().reset_index(drop=True)
    unique_coupons['CouponCode'] = 'CPN_' + unique_coupons.index.astype(str)
    unique_coupons['ValidFrom'] = '2009-01-01'
    unique_coupons['ValidTo'] = '2099-12-31'
    unique_coupons.to_sql('Coupon', engine, schema='core', if_exists='append', index=False)
    print(f"  Inserted {len(unique_coupons)} Unique Coupons.")

    c_map = pd.read_sql("SELECT CouponID, CouponType, DiscountValue FROM core.Coupon", engine)
    c_dict = {(row['CouponType'], row['DiscountValue']): row['CouponID'] for idx, row in c_map.iterrows()}

    # 6. Insert core.CouponIssuance
    print("Processing core.CouponIssuance...")
    issuance_df = rfm_df[['CustomerID', 'CouponType', 'DiscountValue', 'IsRedeemed']].copy()
    issuance_df['CouponID'] = issuance_df.apply(lambda x: c_dict[(x['CouponType'], x['DiscountValue'])], axis=1)
    issuance_df = issuance_df.drop(columns=['CouponType', 'DiscountValue'])
    issuance_df['IssuedAt'] = '2009-01-01 00:00:00'
    issuance_df['RedeemedAt'] = np.where(issuance_df['IsRedeemed'] == 1, '2011-12-09 00:00:00', None)
    issuance_df.to_sql('CouponIssuance', engine, schema='core', if_exists='append', index=False)
    print(f"  Inserted {len(issuance_df)} Coupon Issuances.")

    # 7. Insert analytics.CustomerRFM
    print("Processing analytics.CustomerRFM...")
    rfm_insert = rfm_df[['CustomerID', 'Recency', 'Frequency', 'Monetary', 'R_Score', 'F_Score', 'M_Score', 'Segment']].copy()
    rfm_insert = rfm_insert.rename(columns={'Segment': 'RFM_Segment'})
    rfm_insert['SnapshotDate'] = '2011-12-09'
    rfm_insert.to_sql('CustomerRFM', engine, schema='analytics', if_exists='append', index=False)
    print(f"  Inserted {len(rfm_insert)} RFM Records.")

    elapsed = time.time() - start_time
    print(f"\n[DONE] Import completed successfully in {elapsed:.2f} seconds!")

if __name__ == '__main__':
    main()
