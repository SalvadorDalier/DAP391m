import numpy as np
import pandas as pd
import pytest


class TestUpliftScore:
    def test_uplift_formula(self):
        pred_t = np.array([0.8, 0.3, 0.6])
        pred_c = np.array([0.4, 0.5, 0.2])
        uplift = pred_t - pred_c
        expected = np.array([0.4, -0.2, 0.4])
        np.testing.assert_almost_equal(uplift, expected)

    def test_decile_binning(self):
        scores = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0])
        df = pd.DataFrame({'uplift_score': scores})
        df['decile'] = pd.qcut(df['uplift_score'], 10,
                                labels=np.arange(10, 0, -1))
        assert len(df['decile'].unique()) == 10

    def test_decile_ten_digits(self):
        df = pd.DataFrame({'uplift_score': np.random.randn(100)})
        df['decile'] = pd.qcut(df['uplift_score'], 10,
                                labels=np.arange(1, 11))
        assert df['decile'].nunique() == 10
        assert df['decile'].min() == 1
        assert df['decile'].max() == 10


class TestQiniCalculation:
    def test_qini_sort_descending(self):
        df_test = pd.DataFrame({
            'uplift_score': [0.9, 0.1, 0.5, 0.3],
            'Treatment': [1, 0, 1, 0],
            'Is_Redeemer': [1, 0, 0, 1],
        })
        df_test = df_test.sort_values(by='uplift_score', ascending=False)
        assert df_test['uplift_score'].iloc[0] == 0.9
        assert df_test['uplift_score'].iloc[-1] == 0.1

    def test_qini_cumulative_formula(self):
        df_test = pd.DataFrame({
            'uplift_score': [0.9, 0.7, 0.5, 0.3, 0.1],
            'Treatment': [1, 0, 1, 0, 1],
            'Is_Redeemer': [1, 1, 0, 0, 1],
        })
        df_test = df_test.sort_values(by='uplift_score', ascending=False).reset_index(drop=True)
        df_test['cum_n'] = np.arange(1, len(df_test) + 1)
        df_test['cum_treat'] = df_test['Treatment'].cumsum()
        df_test['cum_control'] = df_test['cum_n'] - df_test['cum_treat']
        df_test['cum_y_treat'] = (df_test['Is_Redeemer'] * df_test['Treatment']).cumsum()
        df_test['cum_y_control'] = (df_test['Is_Redeemer'] * (1 - df_test['Treatment'])).cumsum()
        n_t = df_test['Treatment'].sum()
        n_c = len(df_test) - n_t
        df_test['qini'] = df_test['cum_y_treat'] - df_test['cum_y_control'] * (n_t / n_c)
        assert df_test['qini'].iloc[0] >= 0

    def test_qini_monotonic_increasing(self):
        df_test = pd.DataFrame({
            'uplift_score': [0.9, 0.7, 0.5, 0.3, 0.1],
            'Treatment': [1, 1, 0, 0, 1],
            'Is_Redeemer': [1, 1, 0, 0, 0],
        })
        df_test = df_test.sort_values(by='uplift_score', ascending=False).reset_index(drop=True)
        df_test['cum_n'] = np.arange(1, len(df_test) + 1)
        df_test['cum_treat'] = df_test['Treatment'].cumsum()
        df_test['cum_control'] = df_test['cum_n'] - df_test['cum_treat']
        df_test['cum_y_treat'] = (df_test['Is_Redeemer'] * df_test['Treatment']).cumsum()
        df_test['cum_y_control'] = (df_test['Is_Redeemer'] * (1 - df_test['Treatment'])).cumsum()
        n_t = df_test['Treatment'].sum()
        n_c = len(df_test) - n_t
        df_test['qini'] = df_test['cum_y_treat'] - df_test['cum_y_control'] * (n_t / n_c)
        for i in range(1, len(df_test)):
            assert df_test['qini'].iloc[i] >= df_test['qini'].iloc[i - 1] - 1e-10


class TestCostBenefit:
    def test_cost_benefit_structure(self):
        cost_per_coupon = 5
        margin = 0.3
        df = pd.DataFrame({
            'uplift_score': [0.9, 0.7, 0.5, 0.3, 0.1],
            'Monetary': [1000, 800, 600, 400, 200],
            'CustomerID': [1, 2, 3, 4, 5],
        })
        df['decile'] = pd.qcut(df['uplift_score'], 10,
                                labels=np.arange(10, 0, -1), duplicates='drop')
        cb_table = df.groupby('decile').agg(
            count=('CustomerID', 'count'),
            uplift_mean=('uplift_score', 'mean'),
            monetary_mean=('Monetary', 'mean'),
        )
        cb_table['total_cost'] = cb_table['count'] * cost_per_coupon
        cb_table['net_profit'] = (cb_table['monetary_mean'] * margin) - cb_table['total_cost']
        cb_table['roi'] = (cb_table['net_profit'] / cb_table['total_cost']) * 100
        assert 'total_cost' in cb_table.columns
        assert 'net_profit' in cb_table.columns
        assert 'roi' in cb_table.columns

    def test_net_profit_positive_for_good_deciles(self):
        cost = 5
        margin = 0.3
        df = pd.DataFrame({
            'uplift_score': [0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05],
            'Monetary': [8000, 7000, 6000, 5000, 4000, 3000, 2000, 1000, 500, 100],
            'CustomerID': range(1, 11),
        })
        df['decile'] = pd.qcut(df['uplift_score'], 10,
                                labels=np.arange(1, 11))
        cb = df.groupby('decile').agg(
            count=('CustomerID', 'count'),
            monetary_mean=('Monetary', 'mean'),
        )
        cb['net_profit'] = (cb['monetary_mean'] * margin) - cb['count'] * cost
        assert cb['net_profit'].max() > cb['net_profit'].min()
        cb['roi'] = np.where(cb['count'] * cost > 0,
                              (cb['net_profit'] / (cb['count'] * cost)) * 100, 0)
        assert 'roi' in cb.columns

    def test_uplift_roc_proxy(self):
        df_test = pd.DataFrame({
            'Is_Redeemer': [1, 0, 1, 0, 1],
            'Treatment': [1, 0, 0, 1, 1],
        })
        df_test['true_uplift_proxy'] = (df_test['Is_Redeemer'] == df_test['Treatment']).astype(int)
        expected = [1, 1, 0, 0, 1]
        assert df_test['true_uplift_proxy'].tolist() == expected


class TestCrossValidation:
    def test_rfm_segments_present(self):
        df = pd.DataFrame({
            'CustomerID': [1, 2, 3, 4, 5],
            'Segment': ['Champions', 'Loyal Customers', 'New Customers', 'At Risk', 'Lost'],
        })
        assert set(df['Segment']) == {'Champions', 'Loyal Customers', 'New Customers', 'At Risk', 'Lost'}

    def test_segment_redemption_rates(self):
        df = pd.DataFrame({
            'Segment': ['Champions', 'Champions', 'Lost', 'Lost'],
            'Is_Redeemer': [1, 0, 0, 0],
        })
        rates = df.groupby('Segment')['Is_Redeemer'].mean()
        assert rates['Champions'] > rates['Lost']
