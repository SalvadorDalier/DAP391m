import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import roc_curve, auc

# --- 1. THIẾT LẬP & TẢI DỮ LIỆU ---
# Đường dẫn đến file train/test đã được tạo từ Bước 2
TRAIN_PATH = 'train_data.csv'
TEST_PATH = 'test_data.csv' 
    
df_train = pd.read_csv(TRAIN_PATH)
df_test = pd.read_csv(TEST_PATH)

# Các đặc trưng dùng để huấn luyện
features = ['Recency', 'Frequency', 'TotalReturns']
target = 'Monetary'
treatment = 'Is_Redeemer'

# --- 2. MÔ HÌNH HÓA UPLIFT (T-LEARNER) ---
# Tách dữ liệu tập train thành nhóm đối chứng (Control) và nhóm can thiệp (Treatment)
train_t = df_train[df_train[treatment] == 1]
train_c = df_train[df_train[treatment] == 0]
    
# Huấn luyện mô hình cho nhóm Treatment
model_t = RandomForestRegressor(n_estimators=100, random_state=42)
model_t.fit(train_t[features], train_t[target])

# Huấn luyện mô hình cho nhóm Control
model_c = RandomForestRegressor(n_estimators=100, random_state=42)
model_c.fit(train_c[features], train_c[target])

# Dự đoán trên tập Test
# Uplift Score = Dự đoán khi có coupon - Dự đoán khi không có coupon
pred_t = model_t.predict(df_test[features])
pred_c = model_c.predict(df_test[features])
df_test['uplift_score'] = pred_t - pred_c

# --- 3. TRỰC QUAN HÓA DỮ LIỆU ---
sns.set(style="whitegrid")
plt.rcParams['figure.titlesize'] = 16

# 3.1 Biểu đồ Uplift Histogram
plt.figure(figsize=(8, 5))
sns.histplot(df_test['uplift_score'], bins=30, kde=True, color='teal')
plt.axvline(0, color='red', linestyle='--')
plt.title('Biểu đồ Uplift Histogram (Phân phối mức tăng trưởng dự đoán)', fontsize=14)
plt.xlabel('Mức tăng trưởng dự đoán (Uplift Score)')
plt.ylabel('Số lượng khách hàng')
plt.savefig('uplift_histogram.png', dpi=300)
plt.close()

# 3.2 So sánh các chỉ số RFM giữa 2 nhóm
plt.figure(figsize=(15, 5))
cols = ['Recency', 'Frequency', 'Monetary']
col_names = {'Recency': 'Ngày gần nhất (Recency)','Frequency': 'Tần suất (Frequency)', 'Monetary': 'Giá trị (Monetary)'}
for i, col in enumerate(cols):
    plt.subplot(1, 3, i+1)
    sns.boxplot(x='Is_Redeemer', y=col, data=df_test, palette='Set2')
    plt.title(f'So sánh {col_names[col]}')
    plt.xlabel('Nhóm (0: Không dùng coupon, 1: Có dùng)')
plt.tight_layout()
plt.savefig('rfm_comparison.png', dpi=300)
plt.close()

# 3.3 Đường cong QINI & ROC Uplift
# Sắp xếp khách hàng theo Uplift Score giảm dần
df_test = df_test.sort_values(by='uplift_score', ascending=False).reset_index(drop=True)

# Tính toán các chỉ số tích lũy cho QINI
df_test['cum_n'] = np.arange(1, len(df_test) + 1)
df_test['cum_treat'] = df_test['Is_Redeemer'].cumsum()
df_test['cum_control'] = df_test['cum_n'] - df_test['cum_treat']
df_test['cum_y_treat'] = (df_test['Is_Redeemer'] * df_test['Monetary']).cumsum()
df_test['cum_y_control'] = ((1 - df_test['Is_Redeemer']) * df_test['Monetary']).cumsum()

# Công thức Qini chuẩn hóa đơn giản
n_t = df_test['Is_Redeemer'].sum()
n_c = len(df_test) - n_t
df_test['qini'] = df_test['cum_y_treat'] - df_test['cum_y_control'] * (df_test['cum_treat'] / df_test['cum_control']).fillna(0)

plt.figure(figsize=(8, 6))
plt.plot(df_test['cum_n'] / len(df_test),
df_test['qini'], label='Đường cong Qini', color='blue', lw=2)
plt.plot([0, 1], [0, df_test['qini'].iloc[-1]], 'k--', label='Ngẫu nhiên (Random)')
plt.title('Biểu đồ QINI (Lợi nhuận tích lũy)', fontsize=14)
plt.xlabel('Tỷ lệ khách hàng được mục tiêu (%)')
plt.ylabel('Lợi nhuận Uplift tích lũy (Monetary)')
plt.legend()
plt.savefig('qini_curve.png', dpi=300)
plt.close()

# Vẽ đường cong ROC Uplift (sử dụng ngưỡng Monetary trung vị làm mốc phản hồi tích cực)
threshold_val = df_test['Monetary'].median()
df_test['is_positive'] = (df_test['Monetary'] > threshold_val).astype(int)
fpr, tpr, _ = roc_curve(df_test['is_positive'], df_test['uplift_score'])
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:0.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2,linestyle='--')
plt.title('Đường cong ROC Uplift', fontsize=14)
plt.xlabel('Tỷ lệ Dương tính giả (FPR)')
plt.ylabel('Tỷ lệ Dương tính thật (TPR)')
plt.legend(loc="lower right")
plt.savefig('uplift_roc.png', dpi=300)
plt.close()
# --- 4. BẢNG PHÂN TÍCH CHI PHÍ - LỢI ÍCH ---
cost_per_coupon = 5  # Giả định chi phí mỗi coupon là $5
margin = 0.3        # Giả định biên lợi nhuận là 30% trên doanh thu Score
df_test['decile'] = pd.qcut(df_test['uplift_score'], 10,
labels=np.arange(10, 0, -1))
cb_table = df_test.groupby('decile').agg({
    'CustomerID': 'count',
    'uplift_score': 'mean',
    'Monetary': 'mean'
}).rename(columns={
    'CustomerID': 'Số lượng khách',
    'uplift_score': 'Uplift TB',
    'Monetary': 'Doanh thu TB'
})

cb_table['Tổng Chi phí'] = cb_table['Số lượng khách'] * cost_per_coupon
cb_table['Doanh thu Uplift'] = cb_table['Số lượng khách'] * cb_table['Uplift TB']
cb_table['Lợi nhuận ròng'] = (cb_table['Doanh thu Uplift'] * margin) - cb_table['Tổng Chi phí']
cb_table['ROI (%)'] = (cb_table['Lợi nhuận ròng'] /
cb_table['Tổng Chi phí']) * 100

print("\n--- Bảng phân tích Chi phí - Lợi ích ---")
print(cb_table)
 
# Trực quan hóa Lợi nhuận ròng theo từng nhóm Decile
plt.figure(figsize=(10, 6))
sns.barplot(x=cb_table.index, y=cb_table['Lợi nhuận ròng'], palette='RdYlGn')
plt.title('Lợi nhuận ròng theo Nhóm Uplift (Decile)', fontsize=14)
plt.xlabel('Nhóm Uplift (1 = Cao nhất, 10 = Thấp nhất)')
plt.ylabel('Lợi nhuận ròng dự kiến ($)')
plt.axhline(0, color='black', linewidth=1)
plt.savefig('cost_benefit_analysis.png', dpi=300)
plt.close()