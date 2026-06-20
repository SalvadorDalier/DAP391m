import pandas as pd
import pytest
from src.preprocessing.features import get_segment, build_rfm_pipeline


class TestGetSegment:
    def test_champions_high(self):
        assert get_segment({'R_Score': 5, 'F_Score': 5, 'M_Score': 5}) == 'Champions'

    def test_champions_low(self):
        assert get_segment({'R_Score': 4, 'F_Score': 4, 'M_Score': 4}) == 'Champions'

    def test_loyal_customers(self):
        assert get_segment({'R_Score': 3, 'F_Score': 5, 'M_Score': 5}) == 'Loyal Customers'

    def test_loyal_with_r2(self):
        assert get_segment({'R_Score': 2, 'F_Score': 4, 'M_Score': 4}) == 'Loyal Customers'

    def test_new_customers(self):
        assert get_segment({'R_Score': 4, 'F_Score': 1, 'M_Score': 2}) == 'New Customers'

    def test_new_customers_low_fm(self):
        assert get_segment({'R_Score': 5, 'F_Score': 2, 'M_Score': 1}) == 'New Customers'

    def test_at_risk(self):
        assert get_segment({'R_Score': 1, 'F_Score': 3, 'M_Score': 3}) == 'At Risk'

    def test_at_risk_r2_f3(self):
        assert get_segment({'R_Score': 2, 'F_Score': 3, 'M_Score': 3}) == 'At Risk'

    def test_lost(self):
        assert get_segment({'R_Score': 1, 'F_Score': 1, 'M_Score': 2}) == 'Lost'

    def test_lost_all_one(self):
        assert get_segment({'R_Score': 2, 'F_Score': 2, 'M_Score': 1}) == 'Lost'

    def test_regular_mid(self):
        assert get_segment({'R_Score': 3, 'F_Score': 3, 'M_Score': 3}) == 'Regular Customers'

    def test_regular_high_r_low_f(self):
        assert get_segment({'R_Score': 5, 'F_Score': 3, 'M_Score': 3}) == 'Regular Customers'

    def test_regular_low_r_high_f_low_m(self):
        assert get_segment({'R_Score': 1, 'F_Score': 3, 'M_Score': 1}) == 'Regular Customers'


class TestRFMCalculation:
    def test_rfm_output_shape(self):
        df = pd.DataFrame({
            'Customer ID': range(1, 11),
            'InvoiceDate': pd.to_datetime([
                '2011-01-01', '2011-02-01', '2011-03-01', '2011-04-01',
                '2011-05-01', '2011-06-01', '2011-07-01', '2011-08-01',
                '2011-09-01', '2011-12-09',
            ]),
            'Invoice': [f'INV{i:03d}' for i in range(1, 11)],
            'Price': [10.0, 20.0, 5.0, 15.0, 8.0, 12.0, 25.0, 3.0, 50.0, 7.0],
            'Quantity': [5, 3, 10, 2, 7, 4, 6, 8, 1, 9],
        })
        rfm = build_rfm_pipeline(df)
        assert len(rfm) == 10

    def test_rfm_columns_present(self):
        df = pd.DataFrame({
            'Customer ID': range(1, 6),
            'InvoiceDate': pd.to_datetime([
                '2011-01-01', '2011-06-01', '2011-12-09',
                '2011-03-15', '2011-09-01',
            ]),
            'Invoice': ['INV001', 'INV002', 'INV003', 'INV004', 'INV005'],
            'Price': [10.0, 20.0, 5.0, 15.0, 8.0],
            'Quantity': [5, 3, 10, 2, 7],
        })
        rfm = build_rfm_pipeline(df)
        expected = {'CustomerID', 'Recency', 'Frequency', 'Monetary',
                    'R_Score', 'F_Score', 'M_Score', 'Segment',
                    'CouponType', 'DiscountValue', 'IsRedeemed'}
        assert expected.issubset(set(rfm.columns))

    def test_column_renames(self):
        df = pd.DataFrame({
            'Customer ID': range(1, 6),
            'InvoiceDate': pd.to_datetime([
                '2011-01-01', '2011-06-01', '2011-12-09',
                '2011-03-15', '2011-09-01',
            ]),
            'Invoice': ['INV001', 'INV002', 'INV003', 'INV004', 'INV005'],
            'Price': [10.0, 20.0, 5.0, 15.0, 8.0],
            'Quantity': [5, 3, 10, 2, 7],
        })
        rfm = build_rfm_pipeline(df)
        assert 'CustomerID' in rfm.columns
        assert 'Recency' in rfm.columns
        assert 'Frequency' in rfm.columns
        assert 'Monetary' in rfm.columns

    def test_rfm_scores_in_range(self):
        df = pd.DataFrame({
            'Customer ID': range(1, 11),
            'InvoiceDate': pd.to_datetime(range(1, 11), origin='2011-01-01', unit='D'),
            'Invoice': [f'INV{i:03d}' for i in range(1, 11)],
            'Price': [10.0, 20.0, 5.0, 15.0, 8.0, 12.0, 25.0, 3.0, 50.0, 7.0],
            'Quantity': [5, 3, 10, 2, 7, 4, 6, 8, 1, 9],
        })
        rfm = build_rfm_pipeline(df)
        for score_col in ['R_Score', 'F_Score', 'M_Score']:
            assert rfm[score_col].between(1, 5).all()

    def test_coupon_data_added(self):
        df = pd.DataFrame({
            'Customer ID': range(1, 11),
            'InvoiceDate': pd.to_datetime(range(1, 11), origin='2011-01-01', unit='D'),
            'Invoice': [f'INV{i:03d}' for i in range(1, 11)],
            'Price': [10.0, 20.0, 5.0, 15.0, 8.0, 12.0, 25.0, 3.0, 50.0, 7.0],
            'Quantity': [5, 3, 10, 2, 7, 4, 6, 8, 1, 9],
        })
        rfm = build_rfm_pipeline(df)
        assert 'CouponType' in rfm.columns
        assert 'DiscountValue' in rfm.columns
        assert 'IsRedeemed' in rfm.columns
        assert rfm['DiscountValue'].isin([5, 10, 15, 20]).all()

    def test_reproducible_seed(self):
        df = pd.DataFrame({
            'Customer ID': range(1, 11),
            'InvoiceDate': pd.to_datetime(range(1, 11), origin='2011-01-01', unit='D'),
            'Invoice': [f'INV{i:03d}' for i in range(1, 11)],
            'Price': [10.0, 20.0, 5.0, 15.0, 8.0, 12.0, 25.0, 3.0, 50.0, 7.0],
            'Quantity': [5, 3, 10, 2, 7, 4, 6, 8, 1, 9],
        })
        rfm = build_rfm_pipeline(df)
        assert rfm['IsRedeemed'].sum() > 0

    def test_monetary_calculation(self):
        df = pd.DataFrame({
            'Customer ID': range(1, 11),
            'InvoiceDate': pd.to_datetime(range(1, 11), origin='2011-01-01', unit='D'),
            'Invoice': [f'INV{i:03d}' for i in range(1, 11)],
            'Price': [10.0, 20.0, 5.0, 15.0, 8.0, 12.0, 25.0, 3.0, 50.0, 7.0],
            'Quantity': [5, 3, 10, 2, 7, 4, 6, 8, 1, 9],
        })
        rfm = build_rfm_pipeline(df)
        assert rfm['Monetary'].iloc[0] > 0
