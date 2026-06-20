# THUYẾT MINH ĐỀ CƯƠNG NGHIÊN CỨU / RESEARCH PROPOSAL

| | |
| :--- | :--- |
| **Tên đề tài / Research Title** | Tiếp thị Mã giảm giá Chính xác trong Bán lẻ Trực tuyến: Cách tiếp cận Suy luận Nhân quả sử dụng T-Learner XGBoost và Kỹ nghệ Đặc trưng RFM |
| **Giảng viên hướng dẫn / Mentor** | TS. Nguyễn Văn A |
| **Nhóm sinh viên thực hiện / Members** | 1. Thu Le (thulvm@fpt.edu.vn)<br>2. Nhu Nguyen (nhunqk@fpt.edu.vn)<br>3. Duc Dat (datddse180784@fpt.edu.vn)<br>4. Ngoc Minh (minhtn1412@gmail.com) |
| **Tóm tắt đề tài / Abstract** | Các chiến dịch tiếp thị mã giảm giá đại trà truyền thống dẫn đến lãng phí ngân sách lớn do nhắm mục tiêu khách hàng một cách bừa bãi. Nghiên cứu này đề xuất một hệ thống tiếp thị mã giảm giá chính xác sử dụng học máy nhân quả (mô hình meta-learner T-Learner XGBoost) kết hợp với kỹ nghệ đặc trưng RFM (Recency, Frequency, Monetary) trên bộ dữ liệu Online Retail II. Hệ thống ước lượng Tác động Can thiệp Trung bình có Điều kiện (CATE) để phân loại khách hàng thành bốn phân khúc tiếp thị thực tế: Persuadables (Thuyết phục được), Sure Things (Chắc chắn mua), Sleeping Dogs (Không làm phiền), và Lost Causes (Không tiềm năng). Chúng tôi triển khai quy trình thông qua Flask REST API để chấm điểm khách hàng theo thời gian thực và một dashboard Streamlit tương tác tích hợp mô phỏng What-If hỗ trợ ra quyết định tiếp thị. Mô hình của chúng tôi đạt Diện tích dưới đường cong Uplift (AUUC) là 0.8830, vượt trội đáng kể so với việc nhắm mục tiêu ngẫu nhiên. |

**Từ khóa / Keywords**: Mô hình Uplift, T-Learner, XGBoost, Phân tích RFM, Tiếp thị chính xác, Suy luận nhân quả, Online Retail II.

---

## 1. Giới thiệu / Introduction

### 1.1. Tình hình nghiên cứu trong và ngoài nước / Literature review
Nghiên cứu quốc tế về khuyến mãi bán lẻ đã chuyển đổi mạnh mẽ từ phân khúc heuristic sang các mô hình dự đoán nâng cao. Trong lịch sử, phân tích RFM (Recency, Frequency, Monetary) do Hughes (1994) phổ biến đã đóng vai trò là nền tảng cho tiếp thị trực tiếp. Trong thập kỷ qua, các nhà nghiên cứu đã tập trung vào học máy nhân quả thay vì các mô hình dự báo phân loại truyền thống. Künzel et al. (2019) đã chính thức hóa các khung mô hình meta-learner (S-Learner, T-Learner, X-Learner) để ước lượng CATE. Mô hình T-Learner sử dụng hai mô hình độc lập cho nhóm đối chứng (Control) và nhóm can thiệp (Treatment), mang lại hiệu quả cao khi bề mặt phản hồi của hai nhóm có sự khác biệt lớn, vốn là một đặc điểm rất phổ biến trong các chiến dịch khuyến mãi.

Tại Việt Nam, sự tăng trưởng bùng nổ của thương mại điện tử đã kéo theo ngân sách tiếp thị khổng lồ. Tuy nhiên, các nghiên cứu trong nước vẫn phụ thuộc nhiều vào gom cụm RFM truyền thống hoặc các mô hình dự báo rời bỏ (churn) đơn giản. Ứng dụng thực tế của mô hình uplift trong ngành bán lẻ Việt Nam còn rất hạn chế, dẫn đến các chiến dịch gửi mã giảm giá đại trà (mass mailing) kém hiệu quả và làm giảm biên lợi nhuận. Nghiên cứu đề xuất của chúng tôi giải quyết khoảng trống này bằng cách áp dụng khung T-Learner XGBoost có khả năng mở rộng cao trên dữ liệu giao dịch thực tế.

### 1.2. Những hạn chế của các nghiên cứu hiện tại / The limitation of current works
Các mô hình học máy thông thường chỉ dự đoán xác suất mua hàng chung, vốn là sự kết hợp giữa xu hướng mua hàng tự nhiên và độ nhạy cảm khuyến mãi. Do đó, chúng thường nhắm mục tiêu vào nhóm chắc chắn mua (Sure Things) và bỏ lỡ nhóm cần thuyết phục (Persuadables), gây lãng phí lớn ngân sách. Bên cạnh đó, các thư viện suy luận nhân quả tiên tiến như CausalML rất khó biên dịch trên môi trường Windows do xung đột thư viện C++. Cuối cùng, các công cụ phân tích hiện tại thiếu tính năng mô phỏng What-If trực quan giúp các nhà quản lý tiếp thị tương tác thử nghiệm ngân sách và ROI trước khi chạy.

### 1.3. Sự cần thiết tiến hành nghiên cứu / The necessity of the research
Nghiên cứu này là cần thiết để xây dựng một khung suy luận nhân quả độc lập, nhẹ nhàng, chạy được trên các môi trường máy tính tiêu chuẩn. Bằng cách tự cấu trúc mô hình T-Learner bằng hai mô hình XGBoost riêng biệt, chúng tôi tránh được các nút thắt biên dịch phần mềm mà vẫn duy trì được sức mạnh dự đoán nhân quả tối ưu. Về mặt khoa học, nghiên cứu đóng góp một đánh giá chi tiết về đường cong Qini và chỉ số AUUC trên dữ liệu giao dịch quy mô lớn. Về mặt thực tiễn, nó cung cấp một quy trình ánh xạ trực tiếp từ điểm CATE sang phân khúc khách hàng thực tế và một dashboard trực quan.

---

## 2. Mục tiêu của đề tài / Research objectives
* **Mục tiêu 1**: Thiết kế pipeline ETL làm sạch dữ liệu bán lẻ thô, xử lý các giá trị ngoại lai thông qua capping bách phân vị 99 và lưu trữ đồng bộ vào SQL Server.
* **Mục tiêu 2**: Xây dựng mô hình T-Learner meta-model thủ công sử dụng bộ phân loại XGBoost kép để tính toán điểm CATE cho từng khách hàng.
* **Mục tiêu 3**: Triển khai mô hình đánh giá đường cong Qini để đo lường hiệu quả chiến dịch so với việc gửi ngẫu nhiên.
* **Mục tiêu 4**: Xây dựng Flask API chấm điểm CATE thời gian thực và dashboard Streamlit mô phỏng What-If ROI hỗ trợ ra quyết định tiếp thị.

---

## 3. Phạm vi nghiên cứu / Research scope
Nghiên cứu tập trung vào các giao dịch từ bộ dữ liệu Online Retail II (2009–2011) từ UCI Machine Learning Repository. Việc phát hành và phản hồi mã giảm giá được mô phỏng để phục vụ phân tích nhân quả. Công nghệ sử dụng giới hạn trong các thư viện python (pandas, scikit-learn, xgboost, SQLAlchemy), Flask server và dashboard Streamlit chạy cục bộ.

---

## 4. Tính khả thi của đề tài / Feasibility of research
Dự án có tính khả thi cực kỳ cao do các cấu trúc cơ sở dữ liệu, script ETL, và mô hình học máy đã được triển khai hoàn chỉnh. Mô hình T-Learner đạt chỉ số AUUC xuất sắc là 0.8830 trên dữ liệu kiểm thử, đồng thời cả REST API và Streamlit app đều đã chạy thử nghiệm thành công. Hệ thống chạy ổn định trên cấu hình máy tính văn phòng thông thường, không yêu cầu phần cứng chuyên dụng đắt tiền.

---

## 5. Cách tiếp cận và phương pháp nghiên cứu / Approach and Method
Hệ thống áp dụng phương pháp phát triển phần mềm mô-đun hóa kết hợp với kiểm thử học máy thực nghiệm. Lớp cơ sở dữ liệu ánh xạ giao dịch vào các bảng SQL. Kỹ nghệ đặc trưng tính toán các điểm số RFM. Trong bước huấn luyện, dữ liệu được tách thành nhóm đối chứng (Control) và nhóm can thiệp (Treatment). Mô hình XGBoost thứ nhất học trên nhóm Control và mô hình thứ hai học trên nhóm Treatment. Điểm CATE là hiệu số xác suất dự đoán của hai mô hình. Đánh giá mô hình qua Qini curve và tích hợp vào Streamlit để tính toán bài toán tài chính tự động dựa trên tham số đầu vào của người dùng.

---

## 6. Kế hoạch thực hiện nghiên cứu / Research plan

| STT | Thời gian / Date | Nhiệm vụ / Task | Kết quả cần đạt / Expected Output | Người thực hiện |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Tuần 1 | Thiết lập DB & Pipeline ETL sạch | Schema cơ sở dữ liệu SQL, script ETL xử lý outliers bách phân vị 99 | Nhóm Nghiên Cứu |
| **2** | Tuần 2 | Kỹ nghệ đặc trưng RFM & Mô hình Baseline | Bảng dữ liệu RFM khách hàng, mô hình Logistic Regression (Acc 98.6%) | Nhóm Nghiên Cứu |
| **3** | Tuần 3 | Xây dựng mô hình T-Learner XGBoost | Mô hình XGBoost Control/Treatment được huấn luyện, dự đoán điểm CATE | Nhóm Nghiên Cứu |
| **4** | Tuần 4 | Đánh giá & Tối ưu hóa mô hình | Đồ thị đường cong Qini và AUUC, biểu đồ mức độ quan trọng của đặc trưng | Nhóm Nghiên Cứu |
| **5** | Tuần 5 | Tích hợp dịch vụ API & Triển khai Dashboard | Flask REST API hoạt động ổn định, Streamlit What-If Dashboard trực quan | Nhóm Nghiên Cứu |

---

## 7. Yêu cầu tài nguyên tính toán / Computational Resource Requirements
Máy tính cá nhân thông thường (8GB RAM, CPU i5 hoặc tương đương) chạy Python 3.8+ và SQL Server. Không yêu cầu tài nguyên đám mây trả phí hay GPU chuyên dụng.

---

## 8. Dự kiến kết quả đề tài / Expected results
Đề tài dự kiến bàn giao một nguyên mẫu ứng dụng tối ưu hóa ngân sách tiếp thị số. Về mặt khoa học, chứng minh được việc chỉ nhắm mục tiêu vào nhóm Persuadables mang lại tỷ suất ROI vượt trội so với gửi đại trà. Các sản phẩm bàn giao gồm: (i) Cơ sở dữ liệu SQL sạch, (ii) các tệp mô hình học máy (.pkl), (iii) ứng dụng Streamlit trực quan, và (iv) Báo cáo khoa học định dạng LaTeX dài 10 trang sẵn sàng cho việc nghiệm thu.

---

## 9. Tài liệu tham khảo / References
1. Künzel, S. R., Sekhon, J. S., Bickel, P. J., & Yu, B. (2019). Metalearners for estimating heterogeneous treatment effects using machine learning. *Proceedings of the National Academy of Sciences*, 116(10), 4156-4165.
2. Hughes, A. M. (1994). *Strategic database marketing*. Probus Publishing Company.
3. Radcliffe, N. J., & Surry, P. D. (2011). Real-world uplift modelling with significance-based uplift trees. *White Paper, Stochastic Solutions*, 28, 1-18.
4. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785-794).
5. Chen, D. (2012). Online Retail II. *UCI Machine Learning Repository*. https://doi.org/10.24432/C5CG6D
