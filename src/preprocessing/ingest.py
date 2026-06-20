import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import numpy as np
from src import config


def load_raw_data() -> pd.DataFrame:
    path = config.RAW_DATA_FILE
    if not path.exists():
        msg = (
            f"File not found: {path}\n\n"
            "Please download the dataset from:\n"
            "https://www.kaggle.com/code/kerneler/starter-uci-online-retail-ii-data-set-75960950-2/"
            "input?select=online_retail_09_10.csv\n\n"
            f"Then place it at: {path}"
        )
        raise FileNotFoundError(msg)
    df = pd.read_csv(path, encoding='utf-8-sig')
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Drop rows with missing CustomerID
    before = len(df)
    df = df.dropna(subset=['CustomerID'])
    if len(df) < before:
        print(f"  Dropped {before - len(df)} rows with missing CustomerID")

    # Drop cancellations (InvoiceNo starting with 'c' or 'C')
    if df['InvoiceNo'].dtype == 'object':
        before = len(df)
        df = df[~df['InvoiceNo'].astype(str).str.startswith(('c', 'C'), na=False)]
        if len(df) < before:
            print(f"  Dropped {before - len(df)} cancellations")

    # Ensure positive Quantity and Price
    price_col = 'UnitPrice' if 'UnitPrice' in df.columns else 'Price'
    df = df[df['Quantity'] > 0]
    df = df[df[price_col] > 0]
    df = df.reset_index(drop=True)

    # Cap outliers at P99
    q99_qty = df['Quantity'].quantile(0.99)
    q99_price = df[price_col].quantile(0.99)
    df['Quantity'] = df['Quantity'].clip(upper=q99_qty)
    df[price_col] = df[price_col].clip(upper=q99_price)

    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mapping = {
        'UnitPrice': 'Price',
        'CustomerID': 'Customer ID',
        'InvoiceNo': 'Invoice',
        'StockCode': 'StockCode',
        'Description': 'Description',
        'Quantity': 'Quantity',
        'InvoiceDate': 'InvoiceDate',
        'Country': 'Country',
    }
    cols = {k: v for k, v in mapping.items() if k in df.columns}
    df = df.rename(columns=cols)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    return df


def load_cleaned_data() -> pd.DataFrame:
    df = load_raw_data()
    df = clean_data(df)
    df = rename_columns(df)
    return df


def validate_data(df: pd.DataFrame) -> None:
    required = {'Invoice', 'Customer ID', 'InvoiceDate', 'Price', 'Quantity'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if df['Customer ID'].isnull().any():
        raise ValueError("null Customer ID found")
    if (df['Quantity'] <= 0).any():
        raise ValueError("non-positive Quantity found")


def get_customer_base(df: pd.DataFrame) -> pd.DataFrame:
    cust = df[['Customer ID', 'Country']].drop_duplicates()
    cust = cust.rename(columns={'Customer ID': 'CustomerID'})
    cust = cust.drop_duplicates(subset=['CustomerID'])
    return cust


def get_transactions(df: pd.DataFrame) -> pd.DataFrame:
    tx = df.groupby(['InvoiceNo', 'Customer ID', 'InvoiceDate']).apply(
        lambda g: pd.Series({'TotalAmount': (g['Quantity'] * g['Price']).sum()})
    ).reset_index()
    tx = tx.rename(columns={'InvoiceNo': 'InvoiceNo', 'Customer ID': 'CustomerID'})
    return tx


def main():
    try:
        df = load_cleaned_data()
        validate_data(df)
        print(f"Loaded {len(df):,} rows, {df['Customer ID'].nunique():,} customers")
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
