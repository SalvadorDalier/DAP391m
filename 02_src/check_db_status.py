import sqlalchemy
import urllib
import pandas as pd

SERVER_NAME = 'localhost'
DATABASE_NAME = 'Project11DB'

def check_data():
    params = urllib.parse.quote_plus(
        f'DRIVER={{SQL Server}};'
        f'SERVER={SERVER_NAME};'
        f'DATABASE={DATABASE_NAME};'
        f'Trusted_Connection=yes;'
    )
    engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    
    tables = ['customers', 'customer_rfm', 'coupon_campaigns', 'coupon_redemptions', 'fact_sales']
    
    for table in tables:
        try:
            count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM [dbo].[{table}]", engine)['cnt'][0]
            print(f"Table {table}: {count} rows")
            if count > 0:
                sample = pd.read_sql(f"SELECT TOP 3 * FROM [dbo].[{table}]", engine)
                print(sample)
                print("-" * 30)
        except Exception as e:
            print(f"Error checking {table}: {e}")

if __name__ == "__main__":
    check_data()
