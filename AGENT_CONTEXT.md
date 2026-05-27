# 🤖 Bối cảnh dự án dành cho AI Agent (Agent Context Guide)

**File này được tạo ra để cung cấp bối cảnh toàn diện cho bất kỳ AI Agent nào khi tham gia vào dự án này. Vui lòng đọc kỹ trước khi thực hiện các thay đổi mã nguồn hoặc phân tích dữ liệu.**

## 1. Tổng quan dự án (Project Overview)
- **Tên dự án**: DAP391 Project - Online Retail II Analysis & Marketing Uplift Modeling.
- **Nguồn dữ liệu**: Bộ dữ liệu `Online Retail II` (từ UCI Machine Learning Repository).
- **Mục tiêu cốt lõi**: Phân tích dữ liệu bán lẻ trực tuyến, trích xuất các đặc trưng RFM (Recency, Frequency, Monetary), và xây dựng mô hình **Uplift Modeling** để tối ưu hóa chiến dịch Marketing. Tính toán ROI khi thực hiện các chiến dịch nhắm mục tiêu (Targeting).

## 2. Cấu trúc thư mục (Directory Structure)
- `01_Docs/`: Tài liệu dự án.
- `02_src/`: Chứa mã nguồn Python chính (API, scripts xử lý dữ liệu).
- `03_Data/`: Chứa dữ liệu đầu ra (outputs) như file `predictions.csv`.
- `04_Model/`: Nơi lưu trữ các mô hình Machine Learning (nếu có).
- `05_visual/`: Chứa dữ liệu trực quan hóa (`test_data.csv`) và file Power BI.
- `06_Final_Reports/`: Các báo cáo tiến độ và kết quả phân tích (Ví dụ: `Step4_Report.md`).

## 3. Logic nghiệp vụ cốt lõi (Core Business Logic)
Dự án sử dụng hai phương pháp để tính toán **Uplift Score**:
1. **Phương pháp Heuristic (Cũ - Baseline cho báo cáo ban đầu)**: Nội suy từ RFM (tại `02_src/export_predictions.py`) để phục vụ mô phỏng kinh doanh khi chưa có mô hình.
2. **Phương pháp Machine Learning (Mới - Bước 5)**: Sử dụng mô hình **T-Learner (XGBoost)** để học quan hệ nhân quả (CATE) dựa trên dữ liệu thật (tại `02_src/models/train_uplift_model.py`). Mô hình này cung cấp điểm Uplift chính xác hơn dựa trên độ nhạy cảm của khách hàng với mã giảm giá.
### Phân khúc khách hàng (Customer Segments)
Khách hàng được chia thành 4 nhóm theo logic Marketing Uplift:
1. **Persuadables (Target)**: Khách hàng chỉ mua nếu được tiếp thị. (Điểm Uplift >= 75) -> **Đây là nhóm duy nhất cần tập trung ngân sách Marketing.**
2. **Sure Things**: Khách đằng nào cũng mua, không cần tiếp thị. (Điểm 50 - 75)
3. **Sleeping Dogs**: Khách sẽ phản ứng tiêu cực nếu bị làm phiền. (Điểm 25 - 50)
4. **Lost Causes**: Khách không bao giờ mua. (Điểm < 25)

### Quy tắc tính toán Uplift_Score hiện tại
File `02_src\export_predictions.py` sử dụng logic sau:
- **Base Tier (Điểm nền)** phụ thuộc vào `Recency`:
  - Recency trung bình (5-10): Tiềm năng cao nhất (Base = 70).
  - Recency thấp (<= 4): Mới mua gần đây (Base = 40).
  - Recency cao (> 10): Đã rời bỏ (Base = 10).
- **Điểm cộng thêm** dựa vào `Frequency` và `Monetary` (được chuẩn hóa thang 0-1, giới hạn ở percentile 90).
- `Uplift_Score = Base + (Trung bình(F, M) * 30)`

## 4. Tích hợp hệ thống (System Integration)
- **Data Xuất ra (Export)**: `export_predictions.py` lưu file dự đoán tại `03_Data\outputs\predictions.csv`.
- **Power BI Dashboard**: 
  - Sử dụng file `predictions.csv` thông qua Python Script import.
  - Tính toán ROI bằng DAX: `Total Cost`, `Expected Revenue`, `ROI %`.
- **Flask REST API (`02_src\app.py`)**:
  - `GET /api/customer/<customer_id>`: Lấy điểm Uplift và phân khúc của 1 khách hàng.
  - `GET /api/top_targets`: Lấy danh sách Top 20% khách hàng nhóm Persuadables (Target).

## 5. Lưu ý cho Agent (Agent Guidelines)
- Khi phân tích hoặc sửa code liên quan đến Uplift, phải tuân thủ phân khúc 4 nhóm trên.
- Không tùy tiện sinh số ngẫu nhiên cho `Uplift_Score`.
- Khi cần thông tin chi tiết về các hàm DAX hoặc cách setup Power BI, hãy tham chiếu file `06_Final_Reports\Step4_Report.md`.
