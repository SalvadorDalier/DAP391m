import pandas as pd
from sklearn.model_selection import train_test_split
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
# script_dir is C:\Users\Lenovo\Desktop\DAP391_project\03_src\data_prep
project_dir = os.path.abspath(os.path.join(script_dir, '../..'))
rfm_path = os.path.join(project_dir, '01_data', 'processed', 'customer_rfm.csv')
train_path = os.path.join(project_dir, '01_data', 'train_test', 'train_data.csv')
test_path = os.path.join(project_dir, '01_data', 'train_test', 'test_data.csv')

print("Đang đọc dữ liệu RFM...")
df = pd.read_csv(rfm_path)

# Đổi tên cột cho khớp với model script
if 'IsRedeemed' in df.columns:
    df.rename(columns={'IsRedeemed': 'Is_Redeemer'}, inplace=True)

# Để tương thích với visualization.py nếu cần (dù train_uplift_model.py không dùng TotalReturns)
if 'TotalReturns' not in df.columns:
    df['TotalReturns'] = 0.0

print(f"Tổng số khách hàng: {len(df)}")
print(f"Số lượng positive (Is_Redeemer=1): {df['Is_Redeemer'].sum()}")

print("Đang chia tập dữ liệu 80/20...")
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['Is_Redeemer'])

# Tạo thư mục nếu chưa có
os.makedirs(os.path.dirname(train_path), exist_ok=True)

train_df.to_csv(train_path, index=False)
test_df.to_csv(test_path, index=False)

print(f"Đã lưu train_data.csv ({len(train_df)} dòng) vào {train_path}")
print(f"Đã lưu test_data.csv ({len(test_df)} dòng) vào {test_path}")
