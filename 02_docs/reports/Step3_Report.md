# Báo cáo Bước 3: Trực quan hóa Dữ liệu Chuyên sâu

Báo cáo này trình bày các kết quả trực quan hóa dữ liệu từ mô hình Uplift (T-Learner) để đánh giá hiệu quả của chiến dịch phát hành coupon.

## 1. Biểu đồ Uplift Histogram
Biểu đồ phân phối mức tăng trưởng (Uplift Score) dự đoán trên tập kiểm thử (Test). 
- Phần lớn khách hàng có Uplift Score > 0, cho thấy họ có khả năng mang lại doanh thu cao hơn khi được nhận coupon so với khi không nhận.
- Những khách hàng có Uplift Score < 0 (Sleeping Dogs) là những người mà nếu gửi coupon, họ sẽ mang lại lợi nhuận âm. Chúng ta cần tránh gửi coupon cho nhóm này.

![Uplift Histogram](../data%20visualization/uplift_histogram.png)

## 2. Biểu đồ tỷ lệ RFM
So sánh các chỉ số R (Recency), F (Frequency) và M (Monetary) giữa nhóm sử dụng coupon (Is_Redeemer = 1) và không sử dụng (Is_Redeemer = 0).
- Biểu đồ này giúp hiểu rõ sự khác biệt về hành vi mua sắm giữa hai nhóm khách hàng.

![RFM Comparison](../data%20visualization/rfm_comparison.png)

## 3. Đường cong QINI và Ý nghĩa Kinh doanh
### Đường cong QINI
Đường cong QINI so sánh lợi nhuận tích lũy giữa việc gửi coupon theo mức độ ưu tiên của mô hình Uplift so với việc gửi ngẫu nhiên.
![QINI Curve](../data%20visualization/qini_curve.png)

### Ý nghĩa Kinh doanh của Đường cong QINI
- **Xác định tỷ lệ khách hàng tối ưu**: Điểm cao nhất trên đường cong QINI cho biết tỷ lệ khách hàng lý tưởng cần nhắm mục tiêu để đạt lợi nhuận Uplift tối đa. Vượt quá điểm này, việc gửi thêm coupon sẽ làm giảm tổng lợi nhuận (do chi phí coupon vượt quá doanh thu tăng thêm hoặc do gửi cho nhóm "Sleeping Dogs").
- **Đánh giá hiệu suất mô hình**: Khoảng cách giữa đường cong QINI của mô hình và đường ngẫu nhiên (Random) thể hiện giá trị gia tăng mà mô hình mang lại. Đường cong càng cong lên trên chứng tỏ mô hình phân loại khách hàng càng xuất sắc.
- **Tối ưu hóa ngân sách**: Đường cong QINI giúp doanh nghiệp quyết định cách phân bổ ngân sách marketing (coupon) vào đúng nhóm khách hàng có khả năng thay đổi hành vi tích cực nhất (Persuadables), tránh lãng phí vào nhóm chắc chắn mua (Sure Things) hoặc nhóm phản tác dụng (Sleeping Dogs).

## 4. Đường cong ROC Uplift
Đường cong ROC đánh giá khả năng phân loại của mô hình Uplift bằng cách sử dụng trung vị giá trị Monetary làm ngưỡng phân loại tích cực.
![Uplift ROC Curve](../data%20visualization/uplift_roc.png)

## 5. Bảng phân tích Chi phí - Lợi ích (Cost-Benefit Analysis)
Đây là bảng tính toán ROI cho 10 nhóm khách hàng (Decile), được sắp xếp theo Uplift Score giảm dần (Decile 1 là nhóm tốt nhất).
- Giả định chi phí: $5/coupon.
- Giả định biên lợi nhuận: 30% doanh thu.

| Nhóm (Decile) | Số lượng khách | Uplift TB ($) | Lợi nhuận ròng ($) | ROI (%) |
|---|---|---|---|---|
| 1 | 85 | 3133.24 | 79472.54 | 18699.42 |
| 2 | 76 | 2720.63 | 61650.44 | 16223.80 |
| 3 | 78 | 2704.50 | 62895.25 | 16126.99 |
| 4 | 102 | 2179.91 | 66195.37 | 12979.48 |
| 5 | 81 | 1523.05 | 36605.18 | 9038.31 |
| 6 | 77 | 873.65 | 19796.32 | 5141.90 |
| 7 | 105 | 77.50 | 1916.28 | 365.01 |
| 8 | 85 | -1479.46 | -38151.23 | -8976.76 |
| 9 | 85 | -4005.67 | -102569.58 | -24134.02 |
| 10 | 89 | -23135.49 | -618162.46 | -138912.91 |

> [!TIP]
> **Nhận xét quan trọng:** Từ bảng trên có thể thấy, việc nhắm mục tiêu (target) các khách hàng thuộc nhóm 1 đến 7 mang lại lợi nhuận ròng dương và ROI cực kỳ cao. Ngược lại, nếu target vào nhóm 8, 9, 10, công ty sẽ chịu khoản lỗ nặng nề (Lợi nhuận ròng âm). Điều này nhấn mạnh sự cần thiết của việc chỉ nhắm mục tiêu vào top 7 nhóm khách hàng tiềm năng nhất.

![Cost Benefit Analysis](../data%20visualization/cost_benefit_analysis.png)
