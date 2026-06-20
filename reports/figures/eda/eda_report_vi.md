# Bước 2: Báo cáo Phân tích Dữ liệu Khám phá (EDA) — Dự đoán Sử dụng Mã giảm giá

## 1. Tóm tắt Làm sạch Dữ liệu
- Số dòng trước khi làm sạch: 1067372
- Số dòng sau khi làm sạch: 779425
- Số dòng bị xóa do thiếu CustomerID: 243007 dòng
- Giới hạn ngoại lai (mức bách phân vị 99): Quantity=144.00, Price=14.95

## 2. Phân bố RFM
| Nhóm Khách hàng (Segment) | Số lượng | Trung bình Recency | Trung bình Frequency | Trung bình Monetary |
|---|---|---|---|---|
| At Risk (Có nguy cơ rời đi) | 1445 | 201.19 | 2.7 | 780.21 |
| Champions (Nhà vô địch) | 1303 | 25.86 | 17.9 | 8590.2 |
| Hibernating (Ngủ đông) | 1458 | 374.47 | 1.31 | 317.65 |
| Lost (Đã mất) | 321 | 572.86 | 1.0 | 135.35 |
| Loyal (Trung thành) | 1351 | 95.59 | 5.56 | 1885.09 |


## 3. Phân tích Tỷ lệ Sử dụng (Redemption)
- Tỷ lệ sử dụng tổng thể: 38.91%
- Tỷ lệ sử dụng cao nhất: Nhóm Champions đạt 71.91%
- Tỷ lệ sử dụng thấp nhất: Nhóm Lost đạt 10.90%
- Loại mã giảm giá (CouponType) có tỷ lệ sử dụng cao nhất: BOGO

## 4. Các Quan sát EDA Chính
- Những khách hàng sử dụng mã giảm giá có khoảng thời gian mua hàng gần đây (Recency) thấp hơn (trung bình: 117.04 so với 255.01 ngày)
- Những khách hàng sử dụng mã giảm giá có tần suất mua hàng cao hơn (trung bình: 9.82 so với 4.04 lần)
- Mức giảm giá (DiscountValue) cao hơn không có mối tương quan đến việc sử dụng mã (hệ số tương quan = 0.01)

## 5. Phân chia Tập Huấn luyện/Kiểm thử (Train/Test Split)
- Ngày chia tách dữ liệu theo thời gian: 2011-11-20
- Tập huấn luyện (Train set): 4703 dòng (2009-12-01 → 2011-11-20)
- Tập kiểm thử (Test set): 1175 dòng (2011-11-20 → 2011-12-09)
- Kiểm tra rò rỉ dữ liệu (Data leakage): ĐẠT (PASSED)

## 6. Cân bằng Lớp (Class Balance)
- Nhãn IsRedeemed=1 (Có sử dụng): 38.91% | Nhãn IsRedeemed=0 (Không sử dụng): 61.09%
- Khuyến nghị sử dụng SMOTE: Không (Double check)
