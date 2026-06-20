import pandas as pd
import numpy as np
from .. import config


def get_segment(row: pd.Series) -> str:
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


def calculate_rfm(df: pd.DataFrame) -> pd.DataFrame:
    ref_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (ref_date - x.max()).days,
        'Invoice': 'nunique',
        'Price': lambda x: (x * df.loc[x.index, 'Quantity']).sum()
    }).reset_index()
    rfm.rename(columns={
        'Customer ID': 'CustomerID',
        'InvoiceDate': 'Recency',
        'Invoice': 'Frequency',
        'Price': 'Monetary'
    }, inplace=True)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], config.RFM_QUINTILES, labels=[5, 4, 3, 2, 1], duplicates='drop').astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), config.RFM_QUINTILES, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], config.RFM_QUINTILES, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)
    rfm['Segment'] = rfm.apply(get_segment, axis=1)
    return rfm


def simulate_coupons(rfm: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.RandomState(config.COUPON_SEED)
    rfm = rfm.copy()
    rfm['CouponType'] = rng.choice(config.COUPON_TYPES, size=len(rfm))
    rfm['DiscountValue'] = rng.choice(config.COUPON_DISCOUNT_VALUES, size=len(rfm))
    rfm['IsRedeemed'] = rng.choice([0, 1], size=len(rfm), p=[1 - config.COUPON_REDEEM_PROB, config.COUPON_REDEEM_PROB])
    return rfm


def build_rfm_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    rfm = calculate_rfm(df)
    rfm = simulate_coupons(rfm)
    return rfm


def main():
    df = pd.read_csv(config.RAW_DATA_FILE)
    rfm = build_rfm_pipeline(df)
    rfm.to_csv(config.RFM_FILE, index=False)
    print(f"RFM saved: {len(rfm)} customers")


if __name__ == '__main__':
    main()
