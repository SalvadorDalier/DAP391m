import pandas as pd
import sqlalchemy
import urllib
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
SERVER_NAME = 'localhost' 
DATABASE_NAME = 'Project11DB'
EXCEL_FILE_PATH = os.path.join('03_Data', 'excel', 'online_retail_09_10 raw.xlsx')
RFM_FILE_PATH = os.path.join('03_Data', 'excel', 'Master_CustomerRFM.xlsx')

def get_connection():
    params = urllib.parse.quote_plus(
        f'DRIVER={{SQL Server}};'
        f'SERVER={SERVER_NAME};'
        f'DATABASE={DATABASE_NAME};'
        f'Trusted_Connection=yes;'
    )
    engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    return engine

def import_all_data():
    try:
        engine = get_connection()
        
        # 1. Import Fact Sales
        print(f"Reading {EXCEL_FILE_PATH}...")
        df = pd.read_excel(EXCEL_FILE_PATH)
        sales_df = pd.DataFrame()
        sales_df['invoice_no'] = df['Invoice'].astype(str)
        sales_df['customer_hash'] = df['Customer ID'].fillna(0).astype(int).astype(str)
        sales_df['quantity'] = df['Quantity']
        sales_df['unit_price'] = df['Price']
        sales_df['invoice_date'] = pd.to_datetime(df['InvoiceDate'])
        sales_df = sales_df[sales_df['customer_hash'] != '0']
        
        # 2. Import Customers & RFM from Master_CustomerRFM.xlsx
        print(f"Reading {RFM_FILE_PATH}...")
        rfm_df = pd.read_excel(RFM_FILE_PATH)
        rfm_df['customer_hash'] = rfm_df['CustomerID'].astype(str)
        
        # Logic phân khúc RFM đơn giản (nếu chưa có trong file)
        # Giả sử: Monetary > 2000 là 'VIP', > 1000 là 'Loyal', còn lại là 'Regular'
        def segment(row):
            if row['Monetary'] > 2000: return 'VIP'
            if row['Monetary'] > 500: return 'Loyal'
            return 'Regular'
        
        rfm_df['rfm_segment'] = rfm_df.apply(segment, axis=1)
        
        # Đẩy dữ liệu vào bảng Customers
        print("Updating Customers table...")
        customers_to_db = rfm_df[['customer_hash', 'rfm_segment']].copy()
        customers_to_db['is_active'] = 1
        # Xóa dữ liệu cũ để tránh lỗi PK hoặc trùng lặp
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("DELETE FROM fact_sales"))
            conn.execute(sqlalchemy.text("DELETE FROM customer_rfm"))
            conn.execute(sqlalchemy.text("DELETE FROM coupon_redemptions"))
            conn.execute(sqlalchemy.text("DELETE FROM customers"))
            conn.commit()
            
        customers_to_db.to_sql('customers', engine, if_exists='append', index=False)
        
        # Đẩy dữ liệu vào bảng Fact Sales
        print("Updating fact_sales table...")
        sales_df.to_sql('fact_sales', engine, if_exists='append', index=False)
        
        # Đẩy dữ liệu vào bảng customer_rfm
        print("Updating customer_rfm table...")
        rfm_to_db = rfm_df[['customer_hash', 'Recency', 'Frequency', 'Monetary']].copy()
        rfm_to_db.columns = ['customer_hash', 'recency', 'frequency', 'monetary']
        rfm_to_db['snapshot_date'] = datetime.now()
        rfm_to_db.to_sql('customer_rfm', engine, if_exists='append', index=False)
        
        # 3. Tạo dữ liệu mẫu cho Coupon Campaign
        print("Creating sample Coupon Campaigns...")
        campaigns = pd.DataFrame([
            {
                'campaign_name': 'Summer Sale 2026',
                'coupon_type': 'Discount',
                'discount_value': 10.00,
                'start_date': datetime.now() - timedelta(days=30),
                'end_date': datetime.now() + timedelta(days=30),
                'budget_gbp': 5000.00,
                'target_segment': 'VIP'
            },
            {
                'campaign_name': 'Welcome Back',
                'coupon_type': 'Fixed',
                'discount_value': 5.00,
                'start_date': datetime.now() - timedelta(days=10),
                'end_date': datetime.now() + timedelta(days=20),
                'budget_gbp': 2000.00,
                'target_segment': 'Regular'
            }
        ])
        campaigns.to_sql('coupon_campaigns', engine, if_exists='append', index=False)
        
        print("--- IMPORT COMPLETED SUCCESSFULLY ---")

    except Exception as e:
        print(f"--- ERROR: {e} ---")

if __name__ == "__main__":
    import_all_data()
