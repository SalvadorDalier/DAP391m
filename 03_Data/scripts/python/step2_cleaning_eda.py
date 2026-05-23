import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

def main():
    print("[STEP 2.0] Initializing directories...")
    os.makedirs('./data/processed/', exist_ok=True)
    os.makedirs('./outputs/step2/', exist_ok=True)
    
    # TASK 2.1 — Data Cleaning
    print("\n[STEP 2.1] Loading dataset...")
    # Assume the raw file is a CSV as it was retrieved in step 1.
    df = pd.read_csv('./data/raw/online_retail_II.csv')
    
    # 2.1.1 Missing CustomerID strategy
    # Why we DROP instead of impute CustomerID:
    # - CustomerID identifies the entity we are predicting for.
    # - Imputing would fabricate a non-existent customer's purchase history.
    # - MCAR assumption: missing IDs are random (cancelled/guest transactions),
    #   not correlated with redemption behaviour.
    # - Decision: DROP rows where CustomerID is null.
    rows_before = len(df)
    
    cust_col = 'Customer ID' if 'Customer ID' in df.columns else 'CustomerID'
    inv_col = 'Invoice' if 'Invoice' in df.columns else 'InvoiceNo'
    
    df = df.dropna(subset=[cust_col])
    dropped_missing = rows_before - len(df)
    print(f"[STEP 2.1] Dropped missing CustomerID. Remaining rows: {len(df)}")
    
    # 2.1.2 Additional cleaning
    df = df[df['Quantity'] > 0]
    df = df[df['Price'] > 0]
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df[cust_col] = df[cust_col].astype(str).str.replace(r'\.0$', '', regex=True)
    df = df.drop_duplicates()
    
    # 2.1.3 Outlier capping at 99th percentile
    for col in ['Quantity', 'Price']:
        p99 = df[col].quantile(0.99)
        df[col] = df[col].clip(upper=p99)
        print(f"[STEP 2.1] {col} capped at p99 = {p99:.2f}")
    
    rows_after = len(df)
    p99_q = df['Quantity'].max() # it was capped
    p99_p = df['Price'].max()    # it was capped
    
    df.to_csv('./data/processed/online_retail_clean.csv', index=False)
    
    # TASK 2.2 — Feature Engineering: RFM Calculation
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    df['TotalSpend'] = df['Quantity'] * df['Price']
    
    rfm = df.groupby(cust_col).agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        inv_col: 'nunique',
        'TotalSpend': 'sum'
    }).rename(columns={'InvoiceDate': 'Recency', inv_col: 'Frequency', 'TotalSpend': 'Monetary'}).reset_index()
    rfm.rename(columns={cust_col: 'CustomerID'}, inplace=True)
    
    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5,4,3,2,1])
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1,2,3,4,5])
    rfm['RFM_Score'] = rfm['R_Score'].astype(int) + rfm['F_Score'].astype(int) + rfm['M_Score'].astype(int)
    
    def rfm_segment(row):
        if row['RFM_Score'] >= 13:
            return 'Champions'
        elif row['RFM_Score'] >= 10:
            return 'Loyal'
        elif row['RFM_Score'] >= 7:
            return 'At Risk'
        elif row['RFM_Score'] >= 4:
            return 'Hibernating'
        else:
            return 'Lost'
            
    rfm['Segment'] = rfm.apply(rfm_segment, axis=1)
    
    rfm.to_csv('./data/processed/customer_rfm.csv', index=False)
    print(f"\n[STEP 2.2] RFM table saved. Shape: {rfm.shape}")
    print(rfm['Segment'].value_counts())
    
    # TASK 2.3 — Simulate Coupon Data & Merge Features
    seg_prob = {
        'Champions':   0.72,
        'Loyal':       0.55,
        'At Risk':     0.28,
        'Hibernating': 0.15,
        'Lost':        0.08
    }

    np.random.seed(42)
    rfm['IsRedeemed'] = rfm['Segment'].map(seg_prob).apply(lambda p: np.random.binomial(1, p))

    coupon_types = ['PERCENTAGE', 'FIXED', 'BOGO', 'FREESHIP']
    rfm['CouponType'] = np.random.choice(coupon_types, size=len(rfm))
    rfm['DiscountValue'] = np.where(
        rfm['CouponType'] == 'PERCENTAGE',
        np.random.choice([10, 15, 20, 25, 30], size=len(rfm)),
        np.random.choice([5, 10, 20, 50], size=len(rfm))
    )

    print(f"\n[STEP 2.3] Redemption rate: {rfm['IsRedeemed'].mean():.2%}")
    print(f"[STEP 2.3] Class balance:\n{rfm['IsRedeemed'].value_counts()}")
    
    # TASK 2.4 — Temporal Train/Test Split
    last_purchase = df.groupby(cust_col)['InvoiceDate'].max().reset_index()
    last_purchase.columns = ['CustomerID', 'LastPurchaseDate']

    master = rfm.merge(last_purchase, on='CustomerID')
    master = master.sort_values('LastPurchaseDate')

    cutoff_idx = int(len(master) * 0.80)
    cutoff_date = master.iloc[cutoff_idx]['LastPurchaseDate']
    print(f"\n[STEP 2.4] Temporal cutoff date: {cutoff_date.date()}")

    train = master[master['LastPurchaseDate'] <= cutoff_date]
    test  = master[master['LastPurchaseDate'] >  cutoff_date]

    print(f"[STEP 2.4] Train size: {len(train)} | Test size: {len(test)}")
    print(f"[STEP 2.4] Train date range: {train['LastPurchaseDate'].min().date()} -> {train['LastPurchaseDate'].max().date()}")
    print(f"[STEP 2.4] Test  date range: {test['LastPurchaseDate'].min().date()} -> {test['LastPurchaseDate'].max().date()}")

    assert train['LastPurchaseDate'].max() <= test['LastPurchaseDate'].min(), "DATA LEAKAGE DETECTED: train/test dates overlap!"

    train.to_csv('./data/processed/train.csv', index=False)
    test.to_csv('./data/processed/test.csv',  index=False)
    
    # TASK 2.5 — EDA: Separate Analysis by IsRedeemed Group
    features = ['Recency', 'Frequency', 'Monetary', 'RFM_Score', 'DiscountValue']
    eda_stats = master.groupby('IsRedeemed')[features].agg(['mean','median','std']).round(2)
    print("\n[STEP 2.5] EDA — Group statistics by IsRedeemed:")
    print(eda_stats.to_string())
    
    # Plots
    print("[STEP 2.5] Generating plots...")
    sns.set_theme(style="whitegrid")
    
    # 1. Box plots
    plt.figure(figsize=(15, 5))
    for i, col in enumerate(['Recency', 'Frequency', 'Monetary'], 1):
        plt.subplot(1, 3, i)
        sns.boxplot(x='IsRedeemed', y=col, data=master)
        plt.title(f'{col} by IsRedeemed')
    plt.tight_layout()
    plt.savefig('./outputs/step2/boxplot_rfm.png')
    plt.close()
    
    # 2. Redemption by Segment
    plt.figure(figsize=(10, 5))
    seg_redemption = master.groupby('Segment')['IsRedeemed'].mean().sort_values(ascending=False)
    sns.barplot(x=seg_redemption.index, y=seg_redemption.values)
    plt.title('Redemption Rate by Segment')
    plt.ylabel('Redemption Rate')
    plt.savefig('./outputs/step2/redemption_by_segment.png')
    plt.close()
    
    # 3. Redemption by CouponType
    plt.figure(figsize=(10, 5))
    c_type_redemption = master.groupby('CouponType')['IsRedeemed'].mean().sort_values(ascending=False)
    sns.barplot(x=c_type_redemption.index, y=c_type_redemption.values)
    plt.title('Redemption Rate by CouponType')
    plt.ylabel('Redemption Rate')
    plt.savefig('./outputs/step2/redemption_by_coupontype.png')
    plt.close()
    
    # 4. Histogram of DiscountValue
    plt.figure(figsize=(10, 5))
    sns.histplot(data=master, x='DiscountValue', hue='IsRedeemed', multiple='dodge', bins=10)
    plt.title('DiscountValue Distribution by IsRedeemed')
    plt.savefig('./outputs/step2/discount_histogram.png')
    plt.close()
    
    # 5. Correlation heatmap
    plt.figure(figsize=(10, 5))
    corr = master[features + ['IsRedeemed']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap')
    plt.savefig('./outputs/step2/correlation_heatmap.png')
    plt.close()
    
    # TASK 2.6 — SMOTE Check
    counts = Counter(train['IsRedeemed'])
    minority_ratio = counts[1] / sum(counts.values()) if counts[1] < counts[0] else counts[0] / sum(counts.values())
    
    print(f"\n[STEP 2.6] Class ratio — Redeemed: {minority_ratio:.2%}")

    if minority_ratio < 0.30:
        print("[STEP 2.6] WARNING: Class imbalance detected (<30% minority).")
        print("[STEP 2.6] Recommendation: Apply SMOTE in Step 3 before training.")
        print("[STEP 2.6] SMOTE logic: synthetically generates minority class samples")
        print("           by interpolating between existing minority-class feature vectors.")
        print("           Apply ONLY on train set. Never on test set.")
        smote_rec = "Yes"
    else:
        print("[STEP 2.6] Class balance acceptable. SMOTE not required.")
        smote_rec = "No"
        
    # TASK 2.7 — EDA Report (Markdown)
    print("\n[STEP 2.7] Generating EDA Report...")
    
    rfm_dist = master.groupby('Segment').agg(
        Count=('CustomerID', 'count'),
        Avg_Recency=('Recency', 'mean'),
        Avg_Frequency=('Frequency', 'mean'),
        Avg_Monetary=('Monetary', 'mean')
    ).round(2).reset_index()
    
    rfm_table = "| Segment | Count | Avg Recency | Avg Frequency | Avg Monetary |\n|---|---|---|---|---|\n"
    for _, row in rfm_dist.iterrows():
        rfm_table += f"| {row['Segment']} | {row['Count']} | {row['Avg_Recency']} | {row['Avg_Frequency']} | {row['Avg_Monetary']} |\n"
        
    overall_redemption = master['IsRedeemed'].mean() * 100
    highest_seg = seg_redemption.index[0]
    highest_seg_val = seg_redemption.iloc[0] * 100
    lowest_seg = seg_redemption.index[-1]
    lowest_seg_val = seg_redemption.iloc[-1] * 100
    highest_coupon = c_type_redemption.index[0]
    
    rec_1 = master[master['IsRedeemed']==1]['Recency'].mean()
    rec_0 = master[master['IsRedeemed']==0]['Recency'].mean()
    rec_diff = "lower" if rec_1 < rec_0 else "higher"
    
    freq_1 = master[master['IsRedeemed']==1]['Frequency'].mean()
    freq_0 = master[master['IsRedeemed']==0]['Frequency'].mean()
    freq_diff = "more" if freq_1 > freq_0 else "less"
    
    corr_disc = corr.loc['DiscountValue', 'IsRedeemed']
    disc_corr = "does" if abs(corr_disc) > 0.1 else "does not"
    
    report_content = f"""# Step 2: EDA Report — Coupon Redemption Prediction

## 1. Data Cleaning Summary
- Rows before cleaning: {rows_before}
- Rows after cleaning: {rows_after}
- Missing CustomerID dropped: {dropped_missing} rows
- Outliers capped (p99): Quantity={p99_q:.2f}, Price={p99_p:.2f}

## 2. RFM Distribution
{rfm_table}

## 3. Redemption Rate Insights
- Overall redemption rate: {overall_redemption:.2f}%
- Highest redemption: {highest_seg} at {highest_seg_val:.2f}%
- Lowest redemption: {lowest_seg} at {lowest_seg_val:.2f}%
- CouponType with highest redemption: {highest_coupon}

## 4. Key EDA Observations
- Redeemed customers have {rec_diff} Recency (mean: {rec_1:.2f} vs {rec_0:.2f} days)
- Redeemed customers purchase {freq_diff} frequently (mean: {freq_1:.2f} vs {freq_0:.2f} times)
- Higher DiscountValue {disc_corr} correlate with redemption (correlation = {corr_disc:.2f})

## 5. Train/Test Split
- Temporal cutoff date: {cutoff_date.date()}
- Train set: {len(train)} rows ({train['LastPurchaseDate'].min().date()} → {train['LastPurchaseDate'].max().date()})
- Test set:  {len(test)} rows ({test['LastPurchaseDate'].min().date()} → {test['LastPurchaseDate'].max().date()})
- Data leakage check: PASSED

## 6. Class Balance
- IsRedeemed=1: {(master['IsRedeemed'] == 1).mean()*100:.2f}% | IsRedeemed=0: {(master['IsRedeemed'] == 0).mean()*100:.2f}%
- SMOTE recommendation: {smote_rec}
"""
    with open('./outputs/step2/eda_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    outputs = [
        './data/processed/online_retail_clean.csv',
        './data/processed/customer_rfm.csv',
        './data/processed/train.csv',
        './data/processed/test.csv',
        './outputs/step2/eda_report.md',
        './outputs/step2/boxplot_rfm.png',
        './outputs/step2/redemption_by_segment.png',
        './outputs/step2/redemption_by_coupontype.png',
        './outputs/step2/discount_histogram.png',
        './outputs/step2/correlation_heatmap.png',
    ]
    print("\n[FINAL] Output files:")
    for f in outputs:
        status = "[OK]" if os.path.exists(f) else "[MISSING]"
        print(f"  {status}  {f}")

if __name__ == "__main__":
    main()
