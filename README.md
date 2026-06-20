# Báo Cáo Tổng Hợp Dự Án: Phân Tích Bán Lẻ Trực Tuyến & Marketing Uplift Modeling

## 1. Tổng Quan Dự Án
Dự án **DAP391m** hướng đến việc giải quyết bài toán tiếp thị chính xác (Precision Marketing) trên tập dữ liệu **Online Retail II**. Thay vì chỉ dự đoán xem khách hàng có mua hàng hay không (như bài toán Churn/Conversion thông thường), dự án sử dụng **Uplift Modeling** để xác định độ nhạy cảm của khách hàng đối với các chiến dịch khuyến mãi (mã giảm giá/coupon). Mục tiêu cốt lõi là tối đa hóa ROI (Tỷ suất hoàn vốn) bằng cách chỉ nhắm mục tiêu vào nhóm **Persuadables** (khách hàng chỉ mua khi có khuyến mãi), đồng thời tránh lãng phí ngân sách vào nhóm **Sure Things** (đằng nào cũng mua) và tránh làm phiền nhóm **Sleeping Dogs** (sẽ hủy đăng ký nếu bị làm phiền).

---

## 2. Tiền Xử Lý Dữ Liệu (Python) & Tích Hợp SQL Server
Bước quan trọng nhất để đảm bảo chất lượng dữ liệu đầu vào cho mô hình là loại bỏ nhiễu và xử lý các giá trị bất thường (outliers). Trong file `import_to_sql.py`, quá trình này được thực hiện chặt chẽ qua các bước:

### a. Xử lý CustomerID bị thiếu
Trong ngành bán lẻ trực tuyến, các giao dịch không có `CustomerID` (thường là khách vãng lai không đăng nhập) không thể dùng để phân tích hành vi người dùng (RFM) hay Uplift Modeling. Do đó, script sử dụng pandas để tiền xử lý file CSV thô và loại bỏ các dòng `CustomerID` bị rỗng ngay từ đầu.

### b. Giới hạn Outlier (Percentile Capping) cho Quantity và UnitPrice
Dữ liệu thương mại điện tử thường chứa các giao dịch đột biến (mua sỉ số lượng khổng lồ hoặc nhập sai giá trị). Để giảm thiểu tác động tiêu cực của các giá trị ngoại lai (outliers) lên thuật toán Machine Learning mà không làm mất hoàn toàn thông tin giao dịch, dữ liệu được giới hạn (capping) ở bách phân vị thứ 99 (99th percentile). Ví dụ: `Quantity` và `Price` vượt quá ngưỡng này sẽ bị kéo xuống bằng đúng giá trị ở ngưỡng P99.

### c. Chèn dữ liệu tự động vào SQL Server
Dữ liệu sau khi làm sạch được ánh xạ theo cấu trúc Entity-Relationship của database (gồm `core.Customer`, `core.Transaction`, `core.TransactionItem`, `core.Coupon`). Script sử dụng `sqlalchemy` kết hợp với `pyodbc` và driver `ODBC Driver 18 for SQL Server`. 
- Tính năng `fast_executemany=True` được kích hoạt để đảm bảo việc `to_sql` (chèn hàng chục nghìn records) vào SQL Server diễn ra với tốc độ rất nhanh.
- Transaction mapping: Đảm bảo quan hệ khóa ngoại (Foreign Key) giữa `InvoiceNo` và `TransactionID` được bảo toàn nguyên vẹn trước khi đẩy vào bảng `TransactionItem`.

---

## 3. Tối Ưu Hóa Các Chỉ Số Quan Trọng & Tránh Dư Thừa
Để đảm bảo mô hình Machine Learning chạy nhanh và không dự đoán lệch (bias) vì dữ liệu rác, một số phương pháp tối ưu đã được áp dụng:
- **Ngăn chặn Rò rỉ dữ liệu (Data Leakage):** Thay vì sử dụng `train_test_split(shuffle=True)` để chia dữ liệu ngẫu nhiên, hệ thống sử dụng *Chronological Split* (Chia theo trình tự thời gian, 80% thời gian đầu làm train, 20% sau làm test). Điều này mô phỏng thực tế: dùng dữ liệu quá khứ để dự đoán tương lai, tránh việc mô hình "nhìn trộm" thông tin tương lai.
- **Loại bỏ đặc trưng dư thừa (Feature Selection):** Mô hình không nhồi nhét toàn bộ các cột dữ liệu. Thay vào đó, nó cô đọng toàn bộ lịch sử mua hàng thành 3 chỉ số tinh túy nhất: **Recency** (độ mới), **Frequency** (tần suất), và **Monetary** (giá trị).
- **Giám sát sự quá khớp (Overfitting):** Thiết lập tham số `eval_metric='logloss'` và truyền tập `eval_set` vào XGBoost để theo dõi Loss Curve trên cả tập Train và Test trong quá trình huấn luyện. Nếu Loss của tập test bắt đầu tăng, mô hình đang bị overfit.

---

## 4. Xây Dựng & Tối Ưu Mô Hình Nhắm Mục Tiêu (Targeting Model)
Logic cốt lõi của dự án nằm ở việc dịch chuyển từ Predictive Modeling (Dự đoán thuần túy) sang **Causal Inference (Suy luận nhân quả)**. Mô hình Machine Learning chính được tối ưu hóa để trả lời câu hỏi: *"Khách hàng này sẽ phản ứng thế nào NẾU họ được nhận mã giảm giá, so với NẾU họ KHÔNG nhận được gì?"*

Để làm điều này, hệ thống sẽ gán biến `Treatment` cho những khách hàng nhận được Coupon có `DiscountValue > 5`. Sau đó, bài toán nhắm mục tiêu được tối ưu bằng cách tìm ra sự chênh lệch xác suất mua hàng giữa việc "Bị tác động" (Treatment) và "Không bị tác động" (Control).

---

## 5. Triển Khai T-Learner Bằng XGBoost & Tính Toán Hiệu Suất (QINI, AUUC)
Do gặp khó khăn khi cài đặt thư viện `CausalML` trên hệ điều hành Windows (xung đột dependency), giải pháp đã được refactor để xây dựng mô hình **T-Learner Meta-model thủ công** bằng chính thư viện `xgboost.XGBClassifier` trong file `train_uplift_model.py`.

### a. Kiến trúc T-Learner bằng XGBoost
T-Learner (Two-model Learner) tách dữ liệu ra làm hai nhánh:
1. **Control Model (`xgb_control`):** Huấn luyện trên tập dữ liệu những khách hàng **không** nhận được khuyến mãi (`t_train == 0`).
2. **Treatment Model (`xgb_treatment`):** Huấn luyện trên tập dữ liệu những khách hàng **được** nhận khuyến mãi (`t_train == 1`).

Cả hai mô hình đều dùng cấu trúc cây quyết định (XGBoost) với các siêu tham số được kiểm soát (ví dụ: `max_depth=3`, `n_estimators=100`) để tránh overfit. 
Khi dự đoán cho một khách hàng mới, ta đưa dữ liệu khách hàng đó qua cả 2 mô hình. Điểm Uplift (độ nhạy cảm với khuyến mãi) được tính đơn giản bằng:
`uplift_preds = prob_treatment - prob_control`

### b. Tính toán đường cong Qini và AUUC
Đối với Uplift Modeling, ta không thể dùng Accuracy hay ROC AUC thông thường để đánh giá (vì không ai biết được một khách hàng nếu không nhận khuyến mãi thì sẽ cư xử ra sao trong cùng một thời điểm - *The Fundamental Problem of Causal Inference*). Do đó, dự án tính toán đường cong **Qini** và **AUUC** (Area Under Uplift Curve).

- **Hàm `calculate_qini_curve`**: Sắp xếp khách hàng theo thứ tự `uplift_preds` giảm dần. Bắt đầu nhắm mục tiêu từ người có điểm Uplift cao nhất đến thấp nhất. Ở mỗi ngưỡng, hàm tính số lượng người mua hàng tăng thêm (Incremental Successes) thực tế trong tập test trừ đi số người mua hàng cơ bản (baseline) của nhóm Control.
- **AUUC & Random AUUC**: Tính toán diện tích dưới đường cong Qini (sử dụng `np.trapezoid`). Mô hình chuẩn xác sẽ có đường Qini vọt lên cao ở phía bên trái (chỉ ra rằng ta đang nhắm trúng nhóm Persuadables).
- **QINI Gain**: Là phần diện tích chênh lệch giữa đường cong Uplift của XGBoost (`auuc_score`) so với việc gửi mã giảm giá ngẫu nhiên (`random_auuc`). Trong dự án này, Qini Gain dương và cao minh chứng rằng mô hình ML đã tiết kiệm được chi phí rất lớn so với chiến dịch gửi coupon đại trà.
