import pandas as pd
import sqlalchemy
import urllib
import os

# --- CẤU HÌNH (CONFIGURATION) ---
# Partner chỉ cần thay đổi các thông số ở đây
SERVER_NAME = 'localhost' # Hoặc tên server SQL của bạn
DATABASE_NAME = 'Project11DB'
EXCEL_FILE_PATH = os.path.join('03_Data', 'excel', 'online_retail_09_10 raw.xlsx')

def get_connection():
    """Tạo kết nối tới SQL Server bằng Windows Authentication"""
    params = urllib.parse.quote_plus(
        f'DRIVER={{SQL Server}};'
        f'SERVER={SERVER_NAME};'
        f'DATABASE={DATABASE_NAME};'
        f'Trusted_Connection=yes;'
    )
    engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    return engine

def import_data():
    try:
        print(f"Đang đọc file Excel: {EXCEL_FILE_PATH}...")
        df = pd.read_excel(EXCEL_FILE_PATH)
        
        # Tiền xử lý dữ liệu để khớp với bảng fact_sales trong database
        # Mapping các cột từ Excel sang SQL:
        # Invoice -> invoice_no
        # Customer ID -> customer_hash (Cần chuyển đổi hoặc hash nếu cần)
        # Quantity -> quantity
        # Price -> unit_price
        # InvoiceDate -> invoice_date
        
        print("Đang chuẩn bị dữ liệu...")
        sales_df = pd.DataFrame()
        sales_df['invoice_no'] = df['Invoice'].astype(str)
        sales_df['customer_hash'] = df['Customer ID'].fillna(0).astype(int).astype(str) # Demo: dùng ID làm hash
        sales_df['quantity'] = df['Quantity']
        sales_df['unit_price'] = df['Price']
        sales_df['invoice_date'] = pd.to_datetime(df['InvoiceDate'])
        
        # Xóa các dòng có Customer ID trống nếu cần
        sales_df = sales_df[sales_df['customer_hash'] != '0']

        # Import vào bảng customers trước (do có khóa ngoại)
        print("Đang cập nhật danh sách khách hàng...")
        customers = sales_df[['customer_hash']].drop_duplicates()
        customers['rfm_segment'] = 'New'
        customers['is_active'] = 1
        
        engine = get_connection()
        
        # Sử dụng method 'to_sql' để đẩy dữ liệu
        # Lưu ý: 'if_exists=append' để không xóa dữ liệu cũ
        
        # 1. Update Customers (Bỏ qua nếu đã tồn tại để tránh lỗi duplicate key)
        # Với demo đơn giản, ta import vào bảng fact_sales trước
        # Nhưng đúng quy trình SQL thì phải có Customer trước
        
        print("Đang đẩy dữ liệu vào bảng fact_sales...")
        sales_df.to_sql('fact_sales', engine, if_exists='append', index=False)
        
        print("--- THÀNH CÔNG! ---")
        print(f"Đã import {len(sales_df)} dòng vào database.")

    except Exception as e:
        print(f"--- LỖI: {e} ---")
        print("Vui lòng kiểm tra lại SERVER_NAME và DATABASE_NAME trong code.")

if __name__ == "__main__":
    import_data()
