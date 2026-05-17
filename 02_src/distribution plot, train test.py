import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta

# --- 1. THIẾT LẬP ĐƯỜNG DẪN ---
# Dán đường dẫn Copy as path của bạn vào đây (nhớ giữ chữ r)
path = 'online_retail_09_10.xlsx'

try:
    print("--- Đang bắt đầu quy trình Bước 2 ---")
    # Đọc dữ liệu
    df = pd.read_excel(path)
    
    # --- 2. LÀM SẠCH & XỬ LÝ NGOẠI LAI ---
    # Xóa CustomerID bị thiếu
    df = df.dropna(subset=['CustomerID'])
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Tách dữ liệu: Giao hàng (Quantity > 0) và Trả hàng (Quantity < 0)
    delivered = df[df['Quantity'] > 0].copy()
    returned = df[df['Quantity'] < 0].copy()
    
    # Xử lý ngoại lai bằng bách phân vị 99 (Winsorization)
    q_limit = delivered['Quantity'].quantile(0.99)
    p_limit = delivered['UnitPrice'].quantile(0.99)
    delivered['Quantity'] = delivered['Quantity'].clip(upper=q_limit)
    delivered['UnitPrice'] = delivered['UnitPrice'].clip(upper=p_limit)
    
    # --- 3. FEATURE ENGINEERING (RFM & LABEL) ---
    delivered['TotalSum'] = delivered['Quantity'] * delivered['UnitPrice']
    snapshot_date = delivered['InvoiceDate'].max() + timedelta(days=1)
    
    # Tính RFM
    rfm = delivered.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalSum': 'sum'
    }).rename(columns={'InvoiceDate': 'Recency', 'InvoiceNo': 'Frequency', 'TotalSum': 'Monetary'})
    
    # Nhãn Is_Redeemer (Khách đã từng dùng StockCode 'D')
    coupon_users = delivered[delivered['StockCode'] == 'D']['CustomerID'].unique()
    rfm['Is_Redeemer'] = rfm.index.isin(coupon_users).astype(int)
    
    # Thêm số lần trả hàng
    return_counts = returned.groupby('CustomerID')['InvoiceNo'].nunique()
    rfm['TotalReturns'] = rfm.index.map(return_counts).fillna(0)

    # --- 4. BÁO CÁO EDA (HÌNH ẢNH) ---
    print("--- Đang tạo báo cáo EDA ---")
    sns.set(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # So sánh Recency, Frequency, Monetary giữa 2 nhóm
    cols = ['Recency', 'Frequency', 'Monetary']
    for i, col in enumerate(cols):
        sns.boxplot(x='Is_Redeemer', y=col, data=rfm, ax=axes[i], palette='Set2')
        axes[i].set_title(f'So sánh {col} theo Nhóm Coupon')
        axes[i].set_xlabel('Dùng Coupon (0: Không, 1: Có)')

    plt.tight_layout()
    plt.show() # Hiển thị biểu đồ so sánh
    
    # Vẽ Heatmap tương quan
    plt.figure(figsize=(8, 6))
    sns.heatmap(rfm.corr(), annot=True, cmap='RdBu', fmt='.2f')
    plt.title("Ma trận tương quan giữa các đặc trưng")
    plt.show()

    # Thống kê mô tả
    print("\nThống kê mô tả nhóm dùng Coupon (Is_Redeemer = 1):")
    print(rfm[rfm['Is_Redeemer'] == 1][cols].describe())
    
    # --- 5. CHIA TRAIN/TEST THEO THỜI GIAN (80/20) ---
    # Lấy ngày để chia (dựa trên hóa đơn cuối cùng của mỗi khách)
    # Chúng ta quay lại bảng delivered để lấy mốc thời gian chuẩn
    customer_last_date = delivered.groupby('CustomerID')['InvoiceDate'].max().sort_values()
    split_idx = int(len(customer_last_date) * 0.8)
    train_ids = customer_last_date.index[:split_idx]
    test_ids = customer_last_date.index[split_idx:]
    
    train_set = rfm.loc[train_ids]
    test_set = rfm.loc[test_ids]
    
    # --- 6. XUẤT FILE ---
    rfm.to_csv('Master_CustomerRFM.csv')
    train_set.to_csv('train_data.csv')
    test_set.to_csv('test_data.csv')
    
    print(f"\n--- HOÀN THÀNH BƯỚC 2 ---")
    print(f"Tổng số khách hàng: {len(rfm)}")
    print(f"Số khách dùng coupon: {rfm['Is_Redeemer'].sum()}")
    print(f"Đã lưu: Master_CustomerRFM.csv, train_data.csv, test_data.csv")

except Exception as e:
    print(f"Lỗi: {e}")