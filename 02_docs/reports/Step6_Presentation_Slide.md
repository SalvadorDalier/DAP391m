# Slide Thuyết trình Bước 6: Ứng dụng AI vào Marketing Uplift

*(Lưu ý: Dưới đây là nội dung văn bản (text) được biên soạn sẵn để bạn dễ dàng copy/paste vào các phần mềm làm slide như PowerPoint hoặc Canva)*

---

## Slide 1: Tiêu đề
**ỨNG DỤNG AI ĐỂ TỐI ƯU HÓA CHIẾN DỊCH MARKETING**
- Phân tích Uplift (T-Learner) và Công cụ Hỗ trợ Ra Quyết định
- *Người trình bày: [Tên của bạn]*
- *Dự án: DAP391 - Online Retail II Analysis*

---

## Slide 2: Vấn đề & Giải pháp
**Thực trạng:**
- Gửi coupon đại trà (Mass Mailing) tốn kém và lãng phí ngân sách.
- Không đo lường được ai thực sự thay đổi hành vi nhờ coupon (Uplift).

**Giải pháp với AI:**
- Ứng dụng mô hình **Machine Learning (XGBoost T-Learner)** dự đoán chính xác xác suất khách hàng mua hàng tăng thêm nhờ coupon (CATE).
- Xây dựng **Dashboard AI (Streamlit)** tương tác thời gian thực để tự động lọc tập khách hàng cần gửi.

---

## Slide 3: Tính năng của AI Dashboard
**1. Thanh trượt mô phỏng (What-If Slider):**
- Cho phép người dùng tùy chỉnh "Chi phí Coupon" và "Biên Lợi Nhuận".
- Lợi nhuận kỳ vọng được AI tính toán lại theo từng giây.

**2. Khuyến nghị AI (Auto-labeling):**
- Tự động gắn nhãn "TARGET" (Nên gửi) hoặc "DO NOT TARGET" (Bỏ qua).
- Xuất danh sách tập khách hàng tiềm năng nhất.

**3. Tra cứu theo thời gian thực:**
- Phân tích chân dung (RFM) và khả năng phản hồi của từng khách hàng cá nhân.

---

## Slide 4: Executive Summary (Hiệu quả Đầu tư)
*(Chèn hình ảnh Tab 2 của Streamlit Dashboard vào slide này)*

**So sánh Lợi ích (AI vs Đại trà):**
- 📉 **Mass Mailing:** Ngân sách lớn, tỷ lệ ROI thấp do lãng phí vào nhóm "Sure Things" và "Sleeping Dogs".
- 📈 **AI Targeted:** Tiết kiệm đáng kể ngân sách, tập trung vào nhóm "Persuadables". Tối đa hóa Lợi nhuận Ròng và ROI.
- **Kết luận:** Trí tuệ nhân tạo (AI) giúp cá nhân hóa chiến lược phát hành Coupon, mang lại lợi thế cạnh tranh về tài chính và tối ưu hiệu suất Marketing.

---

## Slide 5: Q&A
**Cảm ơn quý vị đã lắng nghe!**
*(Phần Hỏi & Đáp)*
