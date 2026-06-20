
## 📑 Slide 1 — Title Slide ⏱️ [0:00 – 0:30]

Giới thiệu nhóm và chủ để, mục đích chủ đề là làm sao bớt tiêu tốn tiền cho việc gửi coupon cho khách nhưng vẫn tối đa hiệu năng kinh tế trong việc gửi coupon
---
## 📑 Slide 2 — Outline ⏱️ [0:30 – 0:50]
Nói các phần làm
---
## 📑 Slides 3–4 — Research Questions ⏱️ [0:50 – 1:50]

Trong đời sống, sẽ có rất nhiều trường hợp các công ty bán hàng dùng chiến dich gửi coupon cho khách hàng để kích thích việc mua sắm, tăng hiệu năng kinh tế của công ty. Trong bài nghiên cứu này, ta đặt ra các câu hỏi 

> **RQ1:** Làm thế nào chúng ta có thể ước lượng và phân loại khách hàng bằng cách sử dụng các chỉ số RFM — tức là các chỉ số về tính gần đây, tần suất và giá trị tiền tệ — dựa trên lịch sử giao dịch của họ? Và việc gửi coupon có ảnh hưởng gì tới hành vi mua hàng của khách hay không?

> **RQ2:** Liệu chúng ta có thể ước tính sự tác động của việc phân phối coupon đối với quyết định mua hàng không? Và liệu kiến ​​trúc T-Learner XGBoost có hiệu quả hơn phương pháp truyền thống không?

> **RQ3:** Chiến lược tăng doanh thu bằng AI có thể tiết kiệm được bao nhiêu chi phí so với phương pháp gửi thư hàng loạt, và mức độ cải thiện lợi lợi nhuận là bao nhiêu?

> Mục tiêu khách hàng:`IsRedeemed` và `IsnotRedeemed` --> Mô hình sử dụng: phân loại với nâng cao hiệu quả

## 📑 Slide 5 — Problem Understanding (Step 1) ⏱️ [1:50 – 2:30]

> Ở bước 1, chúng ta đã xác định đây là một bài toán phân loại và nâng cao hiệu quả. Input: tổng số lượng mua hàng, bảng thống kê RFM của các khách hàng, từ đó ta có thể phân loại được các khách thân thiết

> Bối cảnh là **tối ưu hóa khuyến mãi thương mại điện tử** — mục tiêu là loại bỏ lãng phí vốn từ các chiến dịch phân phối đại trà bằng cách xác định và nhắm mục tiêu vào những người tiêu dùng "có thể thuyết phục".

> Mục tiêu: tối đa hóa AUUC (độ chính xác của mô hình) và duy trì độ chính xác phân loại cơ sở vững chắc.

---

## 📑 Slide 6 — Data Understanding (Step 2) ⏱️ [2:30 – 3:20]

> Dataset nhóm sử dụng cho bài nghiên cứu: **Online Retail II** dataset. Sau khi làm sạch dữ liệu, chúng tôi đã giữ lại **779.425 bản ghi** từ **5.878 khách hàng khác nhau**.

> Những vấn đề data và cách xử lý
> - Những dữ liệu nào có customerID bị null thì sẽ bị loại bỏ luôn
> - Có những dữ liệu bị lẫn vào như việc return chứa gồm số âm và dương --> chia ra làm 2 bảng âm và dương với bảng âm chứa dữ liệu return bị âm (do trả hàng)
---

## 📑 Slide 7 — Feature Understanding / EDA (Step 3) ⏱️ [3:20 – 3:50]

> Trong giai đoạn EDA của chúng tôi, chúng tôi đã thực hiện ba cấp độ phân tích:

> - Dùng boxplots để hiểu phân phối RFM.
> - Dùng ROC curve để kiểm tra độ chính xác mô hình
> - Dùng decile và histogram đề coi thử lợi nhuận thu được khi gửi coupon cho các khách hàng
---

## 📑 Slides 8–9 — Feature Engineering (Step 4) ⏱️ [3:50 – 4:30]

> Tiếp theo chúng ta sẽ qua bước 4

> 1. Xử lý outliner: xóa các khách hàng thiếu customerID
> 2. Chuyển hóa từ dữ liệu trong dataset sang bảng RFM
> 3. Chọn các feature cần thiết để cho model chạy như giá tiền bỏ ra hay số hàng mua

> Việc trên chỉ được thực hiện trong môi trường simulation nên có thể sẽ tệ ở ngoài đời
---

## 📑 Slides 10–11 — Visualization & Dashboard ⏱️ [4:30 – 5:10]

> Thì sau khi nhóm đã thực hiện và cho model chạy xong, nhóm em sẽ visualize data để kiểm tra 
> - Heatmap: kiểm tra độ tương quan giữa 3 yếu tố Recency, Monetary, Frequency với tổng lợi nhuận và với hành vi sử dụng coupon
---

## 📑 Slides 12–13 — Dataset Partition & Modeling (Steps 5–6) ⏱️ [5:10 – 6:10]

> Bước 5-6 sẽ là bước phân chia và mô hình hóa dữ liệu

> Step 5 — Phân chia dữ liệu:
> Sử dụng phương pháp phân chia dữ liệu huấn luyện/kiểm tra theo tỷ lệ 80/20. Trong số 5.878 khách hàng, **4.703 khách hàng được đưa vào nhóm huấn luyện** và **1.175 khách hàng được đưa vào nhóm kiểm tra**. Phân chia đề việc khách hàng dùng coupon được phân ra đều giữa tập train với test và để ước tính lỗi

> Step 6 — Mô hình hóa dữ liệu:
> Mô hình này sử dụng **hai bộ phân loại XGBoost riêng biệt** — một cho nhóm thử nghiệm, một cho nhóm kiểm tra — để tính toán giá trị CATE của từng khách hàng, đại diện cho sự ảnh hưởng của việc nhận phiếu giảm giá.
---

## 📑 Slide 14 — Evaluation (Step 7) ⏱️ [6:10 – 6:50]

> Sau đó nhóm sẽ đánh giá mô hình ở bước 7

> Mô hình **hồi quy Logistic cơ bản** đạt độ chính xác **70,92%**, với điểm F1 là 65,48% và AUC-ROC là 72,15%.
> Vấn đề nhấn mạnh: Chỉ số ban đầu do AI tạo ra cho thấy độ chính xác 98,61%, đó là một **hallucination**. Nhóm của chúng tôi đã kiểm tra và điều chỉnh thủ công để đưa con số thực tế trở lại mức 70,92%.

---

## 📑 Slide 15 — Hyper-parameter Tuning & Pipeline (Steps 8–9) ⏱️ [6:50 – 7:40]

> Tiếp theo là bước 8 — Tunning:
> Sử dụng **K-Fold cross-validation** để ước lượng lỗi khi chạy trên real data, và thực hiện tối ưu hóa tham số. Hiện tượng overfitting được kiểm soát thông qua chuẩn hóa và ngưỡng độ sâu trong XGBoost.

> Step 9 — Pipeline tốt nhất:
> Tỉnh chỉnh XGBoost vào pipeline của scikit-learn (chống data leakage), sau đó modify các tham số trong training và test
---

## 📑 Slide 16 — AI Service Integration & Application ⏱️ [7:40 – 8:30]
Tiếp theo sẽ là tích hợp AI và công dụng trong đời sống
> Feature chính:
> - Thu thập nhật ký giao dịch và phân tích tự động quy trình xử lý dữ liệu.
> - **Điểm  CATE trực tuyến của từng khách hàng** — nhập vào tên khách hàng để coi điểm uplift
> - Tạo danh sách phân bổ chiến dịch.

> Bảng điều khiển **Streamlit** bao gồm một **trình mô phỏng kinh doanh"** — người dùng có thể điều chỉnh chi phí phiếu giảm giá và các thông số lợi nhuận để xem những thay đổi dự kiến ​​về ROI trong thời gian thực.

> Chúng tôi chọn Flask và Streamlit vì khả năng **tích hợp nhanh chóng** và trình diễn trực tiếp. Ứng dụng hoạt động đầy đủ chức năng và có thể xử lý các tập tin giao dịch trong quá trình đánh giá này.

---

## 📑 Slides 17–18 — Conclusion & AI Reflection (Step 10) ⏱️ [8:30 – 9:30]

> Bước cuối cùng:
> Kết luận: trả lời các câu RQ

> **RQ1**: Xác nhận rằng hệ thống chấm điểm hành vi RFM giúp phân loại hiệu quả các mức độ tương tác của người tiêu dùng — Khách hàng trung thành và khách hàng đã rời bỏ có tỷ lệ redeem khác nhau đáng kể.

> **RQ2**: T-Learner cung cấp mức tăng **+0,5491 điểm nhắm mục tiêu Qini** đã được xác thực so với các chiến dịch ngẫu nhiên, chứng minh rằng uplift modelling vượt trội hơn các phương pháp truyền thống.

> **RQ3**: Bằng cách chuyển từ các chiến dịch quảng bá tràn lan sang để ý vào các nhóm khách hàng "có thể thuyết phục", các công ty có thể tiết kiệm đáng kể chi phí tiếp thị trong khi vẫn duy trì hoặc cải thiện hiệu quả chiến dịch.

> **AI Audit Log:**
> Chúng tôi đã tổng hợp **15-20 gợi ý phát triển cốt lõi** trên 4 trang tính trong một sổ làm việc Excel. Chúng tôi đã phát hiện và khắc phục thành công **3 lỗi nhận thức sai lệch lớn do AI tạo ra** — đáng chú ý nhất là, AI tuyên bố độ chính xác 98,61% trong khi kết quả được xác minh là 70,92%.

> **Human Delta:**
> Nhóm đã chuyển đổi mô hình dự án từ mô hình dự đoán ai sẽ mua sang mô hình dự đoán việc ai sẽ mua sau khi được nhận coupon.
---

## 📑 Closing ⏱️ [9:30 – 10:00]

> Summary: Dự án của chúng tôi chứng minh rằng **mô hình dự đoán hành vi khách hàng dựa trên RFM feature** có thể thay thế các chiến dịch phát phiếu giảm giá hàng loạt bằng việc nhắm vào mục tiêu chính xác. Quy trình T-Learner XGBoost mang lại "Qini gain" có thể đo lường được, và giúp người dùng doanh nghiệp có thể áp dụng điều này một cách hiệu quả..
