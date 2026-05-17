import pandas as pd
from sqlalchemy import create_engine
import urllib
import os
import time

# --- CẤU HÌNH ---
excel_path = r'C:\Users\Lenovo\Downloads\03_Data-20260517T034620Z-3-001\03_Data\online_retail_09_10 raw.xlsx'
server = 'DESKTOP-NAN6FPF'
database = 'Project11DB'
table_name = 'online_retail'

def run_reports():
    print(f"\n{'='*20} ĐANG TẠO BÁO CÁO SQL {'='*20}")
    # Dùng chuỗi kết nối an toàn
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    params = urllib.parse.quote_plus(conn_str)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    queries = {
        "1. TỔNG QUAN HIỆU SUẤT": """
            SELECT 
                ROUND(SUM(Quantity * UnitPrice), 2) AS [Total Revenue (GBP)],
                COUNT(DISTINCT InvoiceNo) AS [Total Orders],
                COUNT(DISTINCT CustomerID) AS [Total Customers],
                SUM(Quantity) AS [Total Items Sold]
            FROM online_retail;
        """,
        "2. XU HƯỚNG DOANH THU": """
            SELECT 
                FORMAT(CAST(InvoiceDate AS DATETIME), 'yyyy-MM') AS [Month],
                ROUND(SUM(Quantity * UnitPrice), 2) AS [Monthly Revenue]
            FROM online_retail
            GROUP BY FORMAT(CAST(InvoiceDate AS DATETIME), 'yyyy-MM')
            ORDER BY [Month];
        """,
        "3. TOP 10 SẢN PHẨM GIÁ TRỊ": """
            SELECT TOP 10
                StockCode,
                Description,
                ROUND(SUM(Quantity * UnitPrice), 2) AS [Total Sales Value]
            FROM online_retail
            WHERE Description IS NOT NULL
            GROUP BY StockCode, Description
            ORDER BY [Total Sales Value] DESC;
        """,
        "4. PHÂN TÍCH THEO THỊ TRƯỜNG": """
            SELECT 
                Country,
                ROUND(SUM(Quantity * UnitPrice), 2) AS [Revenue],
                COUNT(DISTINCT CustomerID) AS [Customer Count]
            FROM online_retail
            GROUP BY Country
            ORDER BY [Revenue] DESC;
        """
    }

    for title, sql in queries.items():
        print(f"\n>>> {title}")
        try:
            df = pd.read_sql(sql, engine)
            print(df.to_string(index=False))
        except Exception as e:
            print(f"Lỗi khi chạy báo cáo: {e}")

if __name__ == "__main__":
    # Bảng online_retail đã được tạo thành công ở lần chạy trước
    run_reports()
    print(f"\n{'='*20} HOÀN TẤT QUY TRÌNH {'='*20}")
