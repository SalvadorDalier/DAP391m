# Tài liệu Hướng dẫn sử dụng: AI Marketing Uplift Dashboard

Tài liệu này hướng dẫn cách khởi động và sử dụng hệ thống Dashboard AI được xây dựng bằng Streamlit trong Bước 6 của dự án.

## 1. Cách khởi động Dashboard
- Đảm bảo bạn đã cài đặt Python và thư viện Streamlit (`pip install streamlit`).
- Mở Terminal/PowerShell và trỏ tới thư mục gốc của dự án (`DAP391_project`).
- Chạy lệnh sau:
  ```bash
  python -m streamlit run 02_src/streamlit_app.py
  ```
- Dashboard sẽ tự động mở trên trình duyệt tại địa chỉ: `http://localhost:8501`.

## 2. Hướng dẫn các tính năng chính

### Tab 1: Công cụ Target (What-if)
Đây là nơi bạn điều chỉnh chi phí chiến dịch để hệ thống AI quyết định.
1. Kéo thanh trượt **Chi phí 1 Coupon ($)**: Nhập chi phí trung bình để phát hành 1 coupon.
2. Kéo thanh trượt **Biên lợi nhuận kỳ vọng (%)**: Chọn mức tỷ suất lợi nhuận ròng của sản phẩm.
3. Nhìn xuống bảng **Khuyến nghị AI**: Hệ thống sẽ hiển thị tổng số người nên được Target. Danh sách (top 100) những người tốt nhất để gửi coupon sẽ được liệt kê ở bảng bên dưới.

### Tab 2: Executive Summary (Báo cáo Tóm tắt)
Đây là giao diện dành cho Quản lý cấp cao để ra quyết định duyệt ngân sách.
1. Tại đây sẽ hiển thị số liệu So sánh giữa **Gửi đại trà (Mass Mailing)** và **Gửi theo AI (Targeted Mailing)**.
2. Bạn có thể xem các chỉ số:
   - **Tổng ngân sách (Cost)**: Số tiền phải bỏ ra để mua/gửi coupon.
   - **Lợi nhuận ròng dự kiến**: Số tiền thực lãi sau khi trừ chi phí.
   - **ROI (%)**: Tỷ suất hoàn vốn.
3. Đọc phần **Kết luận (màu xanh)** ở dưới cùng để xem AI đã giúp tiết kiệm bao nhiêu tiền rác.

### Tab 3: Tra cứu Khách hàng
Dùng để kiểm tra một cá nhân cụ thể.
1. Nhập `Customer ID` vào ô tìm kiếm (Ví dụ: `12348`).
2. Xem các chỉ số RFM và điểm xác suất `CATE` của khách hàng này.
3. Xem khuyến nghị của AI (Target hay Do Not Target).
