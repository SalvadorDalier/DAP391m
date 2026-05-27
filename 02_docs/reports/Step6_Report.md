# Báo cáo Bước 6: Phát triển Ứng dụng AI (Streamlit Dashboard)

## 1. Tổng quan ứng dụng
Dựa trên yêu cầu của Bước 6, dự án đã phát triển một ứng dụng AI (Dashboard) bằng thư viện **Streamlit (Python)**. Ứng dụng này cho phép mô phỏng nghiệp vụ Marketing thông qua cơ chế "What-If" và tự động dán nhãn khách hàng mục tiêu dựa trên mô hình T-Learner XGBoost (đã huấn luyện ở Bước 5).

## 2. Các chức năng cốt lõi

### 2.1. Công cụ Target và Thanh trượt (What-If Slider)
Người dùng có thể tương tác với hai thanh trượt (slider):
- **Chi phí 1 Coupon ($)**: Giao động từ $1 đến $50.
- **Biên lợi nhuận kỳ vọng (%)**: Giao động từ 5% đến 100%.

**Cơ chế hoạt động:**
Khi người dùng thay đổi giá trị trên thanh trượt, hệ thống sẽ tính toán lại **Lợi nhuận kỳ vọng ròng (Expected Profit Uplift)** cho từng khách hàng theo công thức:
> *Expected Profit = (CATE * Monetary * Margin) - Coupon Cost*

### 2.2. Khuyến nghị AI (Auto-labeling)
Dựa vào công thức tính lợi nhuận ròng trên, AI tự động dán nhãn cho toàn bộ danh sách khách hàng (5878 người):
- **Target (Persuadables)**: Nếu *Expected Profit > 0* (Việc phát coupon mang lại lãi).
- **Do Not Target (Sure Things, Sleeping Dogs, Lost Causes)**: Nếu *Expected Profit <= 0* (Việc phát coupon sẽ gây lỗ hoặc lãng phí).

### 2.3. Trang Executive Summary (Tóm tắt Điều hành)
Trang này so sánh hiệu quả của 2 chiến lược:
1. **Mass Mailing (Gửi đại trà)**: Gửi coupon cho toàn bộ danh sách khách hàng.
2.- **Khuyến nghị AI (Auto-labeling)**: Chỉ gửi coupon cho những khách hàng được dán nhãn "Target".

**Báo cáo Real-time:**
Kết quả so sánh Tổng ngân sách (Cost), Lợi nhuận ròng dự kiến và tỷ lệ hoàn vốn (ROI) được hiển thị song song. Hệ thống kết luận trực tiếp số tiền ngân sách tiết kiệm được nhờ dùng AI thay vì gửi đại trà.

## 3. Kiến trúc hệ thống và Tích hợp mô hình
- **Đầu vào (Data Input)**: Tải dữ liệu khách hàng từ `03_Data/data/processed/customer_rfm.csv`.
- **Mô hình (Model Integration)**: Sử dụng module `pickle` tải file `04_Model/uplift_xgboost_manual.pkl` trực tiếp vào bộ nhớ (Memory).
- **Suy luận (Inference)**: Tính toán điểm `CATE` cho toàn bộ danh sách khách hàng mỗi khi ứng dụng khởi động bằng cơ chế caching (`@st.cache_data`) để tối ưu tốc độ.
- **Hiển thị (Frontend)**: Render giao diện web nhanh chóng và linh hoạt thông qua Streamlit.

## 4. Định hướng nâng cấp trong tương lai (Future Works)
Mặc dù phiên bản hiện tại (MVP) đã đáp ứng xuất sắc các yêu cầu phân tích, để triển khai thực tế trên môi trường doanh nghiệp quy mô lớn, ứng dụng có thể được mở rộng với các tính năng sau:
1. **Kết nối Cơ sở dữ liệu động (Live Database)**: Kết nối trực tiếp với SQL/Data Warehouse (thay vì file CSV) để cập nhật và dự đoán hành vi khách hàng theo thời gian thực (Real-time tracking).
2. **Tính năng Upload/Batch Processing**: Cho phép người dùng tải lên file danh sách khách hàng mới, hệ thống tự động chấm điểm và trích xuất danh sách Target.
3. **Phân quyền và Bảo mật (Authentication & Authorization)**: Tích hợp đăng nhập để giới hạn quyền truy cập (vd: Marketing staff dùng tool Target, C-level xem Executive Summary).
4. **Tích hợp Tự động hóa Marketing**: Nối API với các nền tảng như Mailchimp, SendGrid để gửi mã giảm giá tự động đến danh sách Target ngay trên ứng dụng.
5. **Dashboard theo dõi A/B Testing**: Thu thập kết quả thực tế của chiến dịch để so sánh với dự phóng của mô hình, tạo vòng lặp huấn luyện lại (Continuous Training) để cải thiện độ chính xác.

## 5. Kết luận
Dashboard Streamlit đã hoàn thành xuất sắc yêu cầu của Bước 6, biến mô hình học máy khô khan thành một công cụ hỗ trợ ra quyết định (Decision Support System) trực quan và mang tính ứng dụng cao cho phòng Marketing.
