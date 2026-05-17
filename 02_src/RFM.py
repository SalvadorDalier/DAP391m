import pandas as pd
from datetime import timedelta

path = "cleaned retail data.xlsx"

try:
    print("Đang đọc dữ liệu từ Excel, vui lòng đợi giây lát...")
    df = pd.read_excel(path)
    
    # 2. LÀM SẠCH (Data Cleaning)
    # Loại bỏ các dòng không có CustomerID
    df = df.dropna(subset=['CustomerID'])
    
    # Chuyển đổi định dạng ngày tháng
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # 3. XỬ LÝ NGOẠI LAI (Outliers) - Yêu cầu bách phân vị 99
    # Chỉ lấy các giao dịch có số lượng và đơn giá dương (hàng đã giao)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    
    # Tính ngưỡng bách phân vị 99
    q_limit = df['Quantity'].quantile(0.99)
    p_limit = df['UnitPrice'].quantile(0.99)
    
    # Giới hạn (Clip) các giá trị vượt ngưỡng 99
    df['Quantity'] = df['Quantity'].clip(upper=q_limit)
    df['UnitPrice'] = df['UnitPrice'].clip(upper=p_limit)
    
    # 4. KỸ THUẬT ĐẶC TRƯNG (Feature Engineering)
    # Tính thành tiền (Monetary)
    df['TotalSum'] = df['Quantity'] * df['UnitPrice']
    
    # Xác định ngày "hôm nay" (ngày sau giao dịch cuối cùng 1 ngày)
    snapshot_date = df['InvoiceDate'].max() + timedelta(days=1)
    
    # Tính RFM bằng cách GroupBy theo CustomerID
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days, # Recency
        'InvoiceNo': 'nunique',                                 # Frequency
        'TotalSum': 'sum'                                       # Monetary
    })
    
    # Đổi tên các cột cho rõ ràng
    rfm.rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalSum': 'Monetary'
    }, inplace=True)
    
    # 5. XUẤT KẾT QUẢ
    print("\n--- Báo cáo nhanh bảng CustomerRFM ---")
    print(rfm.head())
    
    # Lưu file để dùng cho Tuần 3 (Hồi quy)
    rfm.to_csv('Master_CustomerRFM.csv')
    print("\nĐã lưu file 'Master_CustomerRFM.csv' thành công!")

except Exception as e:
    print(f"Lỗi: {e}. Hãy kiểm tra lại đường dẫn hoặc định dạng file.")