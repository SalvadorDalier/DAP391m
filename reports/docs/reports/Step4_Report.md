# Báo Cáo Bước 4: Tích hợp Dịch vụ & API

Trong Bước 4 của dự án, chúng ta đã tiến hành tích hợp mô hình dự đoán Uplift vào hệ thống báo cáo và dịch vụ API. Dưới đây là chi tiết các hạng mục đã hoàn thành:

## 1. Luồng dữ liệu Power BI & File Dự Đoán
Chúng ta đã viết một script Python (`02_src\export_predictions.py`) để giả lập và xuất file dự đoán `predictions.csv`. Script này đọc file dữ liệu test hiện có (`test_data.csv`), sau đó tính toán điểm `Uplift_Score` theo **Quy luật Heuristic dựa trên mô hình RFM** (thay vì sinh ngẫu nhiên) và phân loại khách hàng vào 4 nhóm: **Persuadables (Target)**, **Sure Things**, **Sleeping Dogs**, và **Lost Causes**.

**Chi tiết quy luật tính Uplift Score (dựa trên RFM):**
- Tận dụng 3 chỉ số Recency (R), Frequency (F), Monetary (M) từ dữ liệu gốc, trong đó F và M được chuẩn hóa (0-1) để triệt tiêu các giá trị ngoại lệ (outliers).
- **Mức nền tảng (Base Tier) dựa trên Recency:**
  - Khách có **Recency trung bình (5-10)**: Thuộc nhóm tiềm năng cao nhất (chưa mua gần đây nhưng vẫn hoạt động), được cấp mức điểm nền tảng cao nhất (70) -> Tổng điểm thường rơi vào nhóm **Persuadables (75-100)**.
  - Khách có **Recency thấp (<= 4)**: Thuộc nhóm vừa mới mua, có xu hướng tự nhiên mua tiếp, được cấp mức điểm nền tảng trung bình (40) -> Tổng điểm thường rơi vào nhóm **Sure Things (50-75)**.
  - Khách có **Recency cao (> 10)**: Thuộc nhóm ít hoạt động/đã rời bỏ, được cấp mức điểm nền tảng thấp nhất (10) -> Tổng điểm rơi vào nhóm **Sleeping Dogs** (25-50) hoặc **Lost Causes** (<25).
- **Điểm Uplift cuối cùng** = Điểm Nền Tảng (Base) + (Trung bình cộng của F_score, M_score * 30).
- **Đầu ra**: `03_Data\outputs\predictions.csv`

**Giải thích các khái niệm quan trọng:**
- **Uplift Score (Mức độ tác động):** Là điểm số thể hiện mức độ gia tăng khả năng mua hàng của một khách hàng *khi và chỉ khi* họ nhận được tiếp thị (quảng cáo, khuyến mãi). Điểm càng cao nghĩa là hoạt động tiếp thị càng có tác dụng thay đổi quyết định mua của khách hàng đó.
- **Ý nghĩa của 4 phân khúc khách hàng:**
  - **Persuadables (Target - Khách hàng có thể thuyết phục):** Những người *chỉ mua hàng nếu được tiếp thị*. Đây là nhóm **mục tiêu duy nhất**, mang lại ROI cao nhất, và chiến dịch nên dồn toàn bộ nguồn lực vào nhóm này.
  - **Sure Things (Chắc chắn mua):** Những người đằng nào cũng mua hàng kể cả khi không có khuyến mãi/tiếp thị. Việc tốn chi phí chạy quảng cáo cho nhóm này là lãng phí.
  - **Lost Causes (Không thể cứu vãn):** Những người sẽ không bao giờ mua hàng dù có nhận tiếp thị hay không. Gửi quảng cáo cho họ cũng chỉ lãng phí tiền.
  - **Sleeping Dogs (Kẻ ngủ say):** Những người sẽ phản ứng tiêu cực nếu bị làm phiền bởi quảng cáo (ví dụ: bực tức hủy đăng ký, chặn ứng dụng), nhưng nếu không làm phiền thì họ vẫn bình thường. Tuyệt đối không gửi tiếp thị cho nhóm này.

**Cách tải dữ liệu vào Power BI bằng Python script:**
Trong Power BI Desktop, thực hiện các bước sau:
1. Mở **Get Data** -> **More...** -> **Python script**.
2. Dán đoạn mã sau vào hộp thoại Python script:
```python
import pandas as pd
df = pd.read_csv(r"C:\Users\Lenovo\Desktop\DAP391_project\03_Data\outputs\predictions.csv")
```
3. Nhấn **OK** và chọn bảng `df` để tải vào Power BI.

## 2. Các Hàm DAX để Đo ROI trong Power BI
Để xây dựng các trang Dashboard theo dõi chỉ số ROI hiệu quả, bạn có thể sử dụng các hàm DAX (Data Analysis Expressions) sau:

- **Tính tổng chi phí Campaign (Total Campaign Cost)**:
```dax
Total_Cost = COUNTROWS(FILTER('df', 'df'[Segment_Label] = "Persuadables (Target)")) * 5 
// Giả định chi phí tiếp cận mỗi khách hàng là 5 đơn vị tiền tệ
```

- **Tính tổng Doanh thu từ chiến dịch (Total Expected Revenue)**:
```dax
Expected_Revenue = SUMX(FILTER('df', 'df'[Segment_Label] = "Persuadables (Target)"), 'df'[Monetary] * ('df'[Uplift_Score]/100))
```

- **Tính ROI (%)**:
```dax
ROI_Percentage = DIVIDE([Expected_Revenue] - [Total_Cost], [Total_Cost], 0)
```

## 3. Thiết kế Dashboard Power BI
Dashboard cần được thiết kế với 3 trang chính (sử dụng file `.pbix`):
- **Trang 1: Theo dõi ROI (ROI Tracking)**
  - Hiển thị các thẻ (Card) như: Total Customers, Total Cost, Expected Revenue, ROI (%).
  - Biểu đồ Bar/Column chart: so sánh doanh thu dự kiến theo tháng.
- **Trang 2: Danh sách Target (Top 20%)**
  - Sử dụng Table hoặc Matrix để liệt kê danh sách khách hàng thuộc nhóm "Persuadables (Target)".
  - Có thể thêm Slicers để lọc theo mức Uplift Score (VD: chỉ lấy > 80 điểm) hoặc theo Monetary.
- **Trang 3: Phân tích Phân khúc RFM & Uplift**
  - Biểu đồ Scatter Plot: Trục X là Recency, Trục Y là Frequency, kích thước bong bóng là Monetary, phân màu theo `Segment_Label`.
  - Biểu đồ Pie/Donut Chart: Tỷ lệ phần trăm các phân khúc (Persuadables, Sure Things, v.v.).

## 4. Phát triển Flask REST API (Tùy chọn)
Đã phát triển một REST API bằng Flask (`02_src\app.py`) với các endpoints sau:
- **`GET /api/customer/<customer_id>`**: Nhận ID khách hàng và trả về điểm Uplift cùng nhãn phân khúc (Segment).
- **`GET /api/top_targets`**: Trả về danh sách Top 20% khách hàng mục tiêu dựa trên điểm Uplift cao nhất.

**Cách chạy API:**
Mở terminal và chạy lệnh:
```bash
python C:\Users\Lenovo\Desktop\DAP391_project\02_src\app.py
```
Sau đó có thể dùng Postman hoặc trình duyệt truy cập `http://localhost:5000/api/customer/15967` để test.

## 5. Sản phẩm Đầu Ra Cuối Cùng
- File `predictions.csv` đã được lưu tại `03_Data\outputs`.
- Code Python `export_predictions.py` và Flask API `app.py` đã nằm trong `02_src`.
- File report này (`Step4_Report.md`) nằm trong thư mục `06_Final_Reports`.
- *Lưu ý: Bạn cần tự tạo file `.pbix` trong Power BI và tự quay video 2 phút quay demo như yêu cầu bài tập của bạn.*
