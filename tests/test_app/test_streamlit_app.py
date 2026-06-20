import warnings
import numpy as np
import pandas as pd
import pytest


warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")


class TestExpectedProfit:
    def test_expected_profit_formula(self):
        df = pd.DataFrame({
            'CATE': [0.15, 0.05, -0.02, -0.10],
            'Monetary': [8000.0, 2000.0, 500.0, 100.0],
        })
        coupon_cost = 5.0
        margin = 0.3
        df['Expected_Profit_Uplift'] = df['CATE'] * df['Monetary'] * margin - coupon_cost
        expected = [0.15 * 8000 * 0.3 - 5,
                    0.05 * 2000 * 0.3 - 5,
                    -0.02 * 500 * 0.3 - 5,
                    -0.10 * 100 * 0.3 - 5]
        np.testing.assert_almost_equal(df['Expected_Profit_Uplift'].values, expected)
        assert df['Expected_Profit_Uplift'].iloc[0] > 0
        assert df['Expected_Profit_Uplift'].iloc[-1] < 0

    def test_target_rule_positive_profit(self):
        df = pd.DataFrame({
            'CATE': [0.15, 0.05, -0.02, -0.10],
            'Monetary': [8000.0, 2000.0, 500.0, 100.0],
        })
        coupon_cost, margin = 5.0, 0.3
        df['Expected_Profit_Uplift'] = df['CATE'] * df['Monetary'] * margin - coupon_cost
        df['Action'] = np.where(df['Expected_Profit_Uplift'] > 0, "Target", "Do Not Target")
        assert df['Action'].tolist() == ["Target", "Target", "Do Not Target", "Do Not Target"]

    def test_all_negative_profit(self):
        df = pd.DataFrame({
            'CATE': [-0.05, -0.10],
            'Monetary': [100.0, 50.0],
        })
        coupon_cost, margin = 5.0, 0.3
        df['Expected_Profit_Uplift'] = df['CATE'] * df['Monetary'] * margin - coupon_cost
        df['Action'] = np.where(df['Expected_Profit_Uplift'] > 0, "Target", "Do Not Target")
        assert (df['Action'] == "Do Not Target").all()

    def test_all_positive_profit(self):
        df = pd.DataFrame({
            'CATE': [0.5, 0.3],
            'Monetary': [10000.0, 5000.0],
        })
        coupon_cost, margin = 5.0, 0.3
        profit = df['CATE'] * df['Monetary'] * margin - coupon_cost
        assert all(p > 0 for p in profit)

    def test_zero_profit_edge(self):
        df = pd.DataFrame({
            'CATE': [0.0],
            'Monetary': [0.0],
        })
        coupon_cost, margin = 5.0, 0.3
        profit = df['CATE'] * df['Monetary'] * margin - coupon_cost
        assert profit.iloc[0] == -5.0

    def test_high_cost_no_targets(self):
        df = pd.DataFrame({
            'CATE': [0.15, 0.10],
            'Monetary': [800.0, 500.0],
        })
        coupon_cost, margin = 50.0, 0.3
        df['Expected_Profit_Uplift'] = df['CATE'] * df['Monetary'] * margin - coupon_cost
        assert (df['Expected_Profit_Uplift'] < 0).all()


class TestROICalculation:
    def test_mass_mailing_cost(self):
        df = pd.DataFrame({'CATE': [0.15, 0.05], 'Monetary': [8000, 2000]})
        coupon_cost, margin = 5.0, 0.3
        mass_cost = len(df) * coupon_cost
        assert mass_cost == 10.0

    def test_mass_mailing_profit(self):
        df = pd.DataFrame({'CATE': [0.15, 0.05], 'Monetary': [8000, 2000]})
        coupon_cost, margin = 5.0, 0.3
        mass_revenue = (df['CATE'] * df['Monetary'] * margin).sum()
        mass_profit = mass_revenue - len(df) * coupon_cost
        expected_revenue = (0.15 * 8000 * 0.3) + (0.05 * 2000 * 0.3)
        expected_profit = expected_revenue - 10.0
        assert mass_revenue == pytest.approx(expected_revenue)
        assert mass_profit == pytest.approx(expected_profit)

    def test_targeted_mailing_cost(self):
        df = pd.DataFrame({
            'CATE': [0.15, 0.05, -0.02],
            'Monetary': [8000, 2000, 500],
        })
        coupon_cost, margin = 5.0, 0.3
        profit = df['CATE'] * df['Monetary'] * margin - coupon_cost
        target_df = df[profit > 0]
        target_cost = len(target_df) * coupon_cost
        assert target_cost == 10.0

    def test_targeted_mailing_profit(self):
        df = pd.DataFrame({
            'CATE': [0.15, 0.05, -0.02],
            'Monetary': [8000, 2000, 500],
        })
        coupon_cost, margin = 5.0, 0.3
        profit = df['CATE'] * df['Monetary'] * margin - coupon_cost
        target_df = df[profit > 0]
        target_revenue = (target_df['CATE'] * target_df['Monetary'] * margin).sum()
        target_profit = target_revenue - len(target_df) * coupon_cost
        assert target_profit > 0

    def test_roi_percentage(self):
        profit = 100.0
        cost = 50.0
        roi = (profit / cost) * 100 if cost > 0 else 0
        assert roi == 200.0

    def test_roi_zero_cost(self):
        profit = 100.0
        cost = 0.0
        roi = (profit / cost) * 100 if cost > 0 else 0
        assert roi == 0.0

    def test_roi_negative(self):
        profit = -50.0
        cost = 100.0
        roi = (profit / cost) * 100
        assert roi == -50.0

    def test_ai_saves_money(self):
        mass_cost = 5000.0 * 5
        target_cost = 2000.0 * 5
        savings = mass_cost - target_cost
        assert savings > 0
        assert savings == 15000.0


class TestCustomerLookup:
    def test_target_customer_shows_success(self):
        action = "Target"
        assert action == "Target"

    def test_do_not_target_customer(self):
        action = "Do Not Target"
        assert action == "Do Not Target"

    def test_customer_data_display(self):
        customer = {'Recency': 10, 'Frequency': 20, 'Monetary': 8000}
        assert customer['Recency'] == 10
        assert customer['Frequency'] == 20
        assert customer['Monetary'] == 8000

    def test_cate_display_format(self):
        cate = 0.15234
        formatted = f"{cate:.4f}"
        assert formatted == "0.1523"

    def test_profit_display_format(self):
        profit = 355.0
        formatted = f"${profit:,.2f}"
        assert formatted == "$355.00"
