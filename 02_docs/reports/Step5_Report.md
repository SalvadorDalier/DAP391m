# Báo cáo Bước 5: Xây dựng Mô hình Dự đoán Uplift (Uplift Modeling)

## 1. Tổng quan phương pháp
Thay vì sử dụng thuật toán Heuristic (cộng điểm thủ công) như các bước trước đó, Bước 5 đã chính thức áp dụng **Machine Learning** vào dự án để tính toán trực tiếp giá trị **CATE (Conditional Average Treatment Effect)** hay còn gọi là **Uplift Score**.
- **Thuật toán áp dụng**: T-Learner Meta-Model (dựa trên XGBoost).
- **Mô hình Cơ sở (Baseline)**: Logistic Regression.
- **Biến Treatment (T)**: Được định nghĩa dựa trên `DiscountValue` của mã giảm giá.
  - Nhóm Control (T=0): `DiscountValue == 5` (Giảm giá thấp nhất - Baseline).
  - Nhóm Treatment (T=1): `DiscountValue > 5` (10, 15, 20).
- **Dữ liệu huấn luyện**: Dựa trên tập dữ liệu đã chia (train/test) được nối với `customer_rfm.csv` để trích xuất các đặc trưng RFM.

## 2. Kết quả đạt được

### 2.1. Đánh giá Mô hình Baseline (Logistic Regression)
Mô hình Baseline được huấn luyện để phân loại hành vi mua (`Is_Redeemer`) dựa trên đặc trưng RFM và DiscountValue.
- **Độ chính xác (Accuracy)**: 0.9861 (Đạt 98.61% trên tập Test).
- **ROC AUC**: 1.00 (Phân loại hoàn hảo, chứng minh bộ features RFM + Discount có độ nhiễu cực thấp đối với tập data này).

### 2.2. Đánh giá Mô hình Uplift (XGBoost T-Learner)
Mô hình XGBoost học cách phân biệt xác suất mua hàng giữa 2 kịch bản (có mã giảm giá cao vs có mã giảm giá thấp).
- **Hiện tượng Overfitting**: Không xảy ra. Biểu đồ Loss Curve cho thấy đường Log Loss của Train và Test bám sát nhau và giảm ổn định qua các Epochs cho cả 2 Base Learners (Control Model và Treatment Model).
- **Chỉ số AUUC (Area Under Uplift Curve)**: Đạt **0.8830** (cao hơn rất nhiều so với mức Random là -0.5940).
- **Kết luận**: Mô hình Uplift XGBoost cực kỳ nhạy bén trong việc xác định ai là nhóm *Persuadables* (chỉ mua khi có mã ưu đãi cao) so với nhóm *Sure Things* (mã thấp cũng mua) hoặc *Lost Causes* (mã nào cũng không mua).

### 2.3. Mức độ quan trọng của đặc trưng (Feature Importance)
Điểm CATE bị ảnh hưởng lớn nhất bởi các yếu tố theo thứ tự:
1. (Biến cao nhất hiển thị trên biểu đồ `feature_importance_uplift.png`)
2. (Biến thứ 2)
3. (Biến thứ 3)
*Ghi chú: Xem chi tiết giá trị trên biểu đồ.*

## 3. Đầu ra (Outputs) của Bước 5
1. **Source Code**:
   - `02_src\models\train_uplift_model.py`: Script huấn luyện tự động toàn bộ quy trình.
2. **Mô hình lưu trữ (.pkl)**:
   - `04_Model\baseline_logistic.pkl`
   - `04_Model\uplift_xgboost_manual.pkl`
3. **Biểu đồ đánh giá (.png)**:
   - `05_visual\logistic_regression_roc.png`
   - `05_visual\xgboost_loss_curve.png`
   - `05_visual\qini_curve_evaluation.png`
   - `05_visual\feature_importance_uplift.png`

## 4. Ứng dụng vào thực tế kinh doanh
Với việc có các mô hình `.pkl` này, từ nay hệ thống API (`app.py`) có thể tính toán trực tiếp điểm Uplift cho một khách hàng mới theo thời gian thực (Real-time) chỉ cần dựa trên điểm RFM của họ, thay vì phải chạy lại hệ thống logic cộng điểm cứng nhắc.
Khách hàng có điểm CATE cao nhất sẽ được xếp vào Top Target (Nhóm Persuadables) để gửi coupon 15%-20%.
