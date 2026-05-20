import pandas as pd
import sqlalchemy
from urllib.parse import quote_plus
import os
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, '..', '03_Data', 'excel', 'online_retail_09_10 raw.xlsx')
RFM_DATA_PATH = os.path.join(BASE_DIR, '..', '03_Data', 'excel', 'Master_CustomerRFM.xlsx')
SERVER_NAME = 'DESKTOP-NAN6FPF'
DATABASE_NAME = 'Project11DB'

def get_connection():
    params = quote_plus(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={SERVER_NAME};'
        f'DATABASE={DATABASE_NAME};'
        f'Trusted_Connection=yes;'
        f'Encrypt=no;'
    )
    engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    return engine

def clean_and_import():
    try:
        engine = get_connection()
        print(f"--- STARTING REAL DATA IMPORT ---")

        # 1. LOAD DATA
        print(f"Loading raw data from {RAW_DATA_PATH}...")
        df = pd.read_excel(RAW_DATA_PATH)
        
        # 2. DATA CLEANING (Handling Bias: Duplicates, Missing, Outliers)
        initial_count = len(df)
        
        # Remove Duplicates
        df = df.drop_duplicates()
        print(f"Removed {initial_count - len(df)} duplicate rows.")
        
        # Handle Missing CustomerID (Crucial for Foreign Keys)
        missing_customers = df['CustomerID'].isnull().sum()
        df = df.dropna(subset=['CustomerID'])
        print(f"Removed {missing_customers} rows with missing Customer ID.")
        
        # Convert Customer ID to string for consistency
        df['customer_hash'] = df['CustomerID'].astype(int).astype(str)
        
        # Handling Outliers (Quantile Clipping)
        q_limit = df['Quantity'].quantile(0.99)
        p_limit = df['UnitPrice'].quantile(0.99)
        df['Quantity'] = df['Quantity'].clip(lower=0, upper=q_limit)
        df['UnitPrice'] = df['UnitPrice'].clip(lower=0, upper=p_limit)
        print(f"Clipped outliers (Quantity > {q_limit}, Price > {p_limit}).")

        # 3. EXTRACT COUPON DATA (StockCode 'D' = Discount)
        print("Extracting actual coupon redemptions...")
        redemptions_raw = df[df['StockCode'] == 'D'].copy()
        
        # Create a real Campaign to link redemptions
        campaigns = pd.DataFrame([{
            'campaign_name': 'Historical Store Discount',
            'coupon_type': 'Extraction',
            'discount_value': 0.00, # Variable in data
            'start_date': df['InvoiceDate'].min(),
            'end_date': df['InvoiceDate'].max(),
            'budget_gbp': redemptions_raw['UnitPrice'].sum() * -1, # Total discount value
            'target_segment': 'All'
        }])
        
        # 4. PREPARE FACT SALES (Exclude non-product codes)
        non_product_codes = ['POST', 'D', 'DOT', 'M', 'BANK CHARGES', 'C2', 'GIFT']
        sales_df = df[~df['StockCode'].isin(non_product_codes)].copy()
        sales_df = sales_df[sales_df['Quantity'] > 0] # Real sales only

        # 5. PREPARE CUSTOMERS & RFM
        print(f"Loading RFM segments from {RFM_DATA_PATH}...")
        rfm_df = pd.read_excel(RFM_DATA_PATH)
        rfm_df['customer_hash'] = rfm_df['CustomerID'].astype(int).astype(str)
        
        # Simple Logic for Segmentation if missing
        def get_segment(m):
            if m > 2000: return 'Champions'
            if m > 500: return 'Loyal'
            return 'New Customers'
        rfm_df['rfm_segment'] = rfm_df['Monetary'].apply(get_segment)

        # 6. PUSH TO DATABASE (TRANSACTIONAL)
        with engine.connect() as conn:
            print("Cleaning old data...")
            conn.execute(sqlalchemy.text("DELETE FROM fact_sales"))
            conn.execute(sqlalchemy.text("DELETE FROM coupon_redemptions"))
            conn.execute(sqlalchemy.text("DELETE FROM coupon_campaigns"))
            conn.execute(sqlalchemy.text("DELETE FROM customer_rfm"))
            conn.execute(sqlalchemy.text("DELETE FROM customers"))
            conn.commit()

        print("Importing Customers...")
        customers_to_db = rfm_df[['customer_hash', 'rfm_segment']].copy()
        customers_to_db['is_active'] = 1
        customers_to_db.to_sql('customers', engine, if_exists='append', index=False)

        print("Importing RFM Data...")
        rfm_to_db = rfm_df[['customer_hash', 'Recency', 'Frequency', 'Monetary']].copy()
        rfm_to_db.columns = ['customer_hash', 'recency', 'frequency', 'monetary']
        rfm_to_db['snapshot_date'] = datetime.now()
        rfm_to_db.to_sql('customer_rfm', engine, if_exists='append', index=False)

        print("Importing Campaigns...")
        campaigns.to_sql('coupon_campaigns', engine, if_exists='append', index=False)
        
        # Get the ID of the campaign we just created
        campaign_id = pd.read_sql("SELECT campaign_id FROM coupon_campaigns", engine)['campaign_id'][0]

        print("Importing Redemptions...")
        redemptions_to_db = pd.DataFrame()
        redemptions_to_db['campaign_id'] = [campaign_id] * len(redemptions_raw)
        redemptions_to_db['customer_hash'] = redemptions_raw['customer_hash']
        redemptions_to_db['redemption_date'] = pd.to_datetime(redemptions_raw['InvoiceDate'])
        before = len(redemptions_to_db)
        redemptions_to_db = redemptions_to_db.dropna(subset=['customer_hash', 'redemption_date'])
        if before > len(redemptions_to_db):
            print(f"Skipped {before - len(redemptions_to_db)} redemption rows with missing data.")
        valid_hashes = customers_to_db['customer_hash'].unique()
        before_red = len(redemptions_to_db)
        redemptions_to_db = redemptions_to_db[redemptions_to_db['customer_hash'].isin(valid_hashes)]
        if before_red > len(redemptions_to_db):
            print(f"Skipped {before_red - len(redemptions_to_db)} redemption rows with unknown customer_hash.")
        redemptions_to_db.to_sql('coupon_redemptions', engine, if_exists='append', index=False)

        print("Importing Fact Sales...")
        before_sales = len(sales_df)
        sales_df = sales_df[sales_df['customer_hash'].isin(valid_hashes)]
        if before_sales > len(sales_df):
            print(f"Skipped {before_sales - len(sales_df)} sales rows with unknown customer_hash.")
        final_sales = pd.DataFrame()
        final_sales['invoice_no'] = sales_df['InvoiceNo'].astype(str)
        final_sales['customer_hash'] = sales_df['customer_hash']
        final_sales['quantity'] = sales_df['Quantity']
        final_sales['unit_price'] = sales_df['UnitPrice']
        final_sales['invoice_date'] = pd.to_datetime(sales_df['InvoiceDate'])
        final_sales.to_sql('fact_sales', engine, if_exists='append', index=False)

        print(f"--- SUCCESS: Imported {len(final_sales)} sales and {len(redemptions_to_db)} redemptions. ---")

    except Exception as e:
        print(f"--- ERROR: {e} ---")

if __name__ == "__main__":
    clean_and_import()
