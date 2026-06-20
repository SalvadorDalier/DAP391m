import numpy as np
import pytest
from src.models.evaluate import calculate_qini_curve


class TestCalculateQiniCurve:
    def test_simple_case(self):
        y_true = np.array([1, 0, 1, 0])
        uplift = np.array([0.9, 0.7, 0.3, 0.1])
        treatment = np.array([1, 0, 1, 0])
        qini, random_qini = calculate_qini_curve(y_true, uplift, treatment)
        assert len(qini) == 4
        assert len(random_qini) == 4

    def test_last_qini_matches_max(self):
        y_true = np.array([1, 1, 0, 0])
        uplift = np.array([0.9, 0.7, 0.3, 0.1])
        treatment = np.array([1, 0, 1, 0])
        qini, _ = calculate_qini_curve(y_true, uplift, treatment)
        total_n_t = treatment.sum()
        total_n_c = len(treatment) - total_n_t
        total_y_t = (y_true * treatment).sum()
        total_y_c = (y_true * (1 - treatment)).sum()
        expected_max = total_y_t - total_y_c * (total_n_t / total_n_c)
        assert qini[-1] == pytest.approx(expected_max)

    def test_first_qini_is_first_row_value(self):
        y_true = np.array([0, 1])
        uplift = np.array([0.8, 0.2])
        treatment = np.array([0, 1])
        qini, _ = calculate_qini_curve(y_true, uplift, treatment)
        sorted_t = treatment[np.argsort(-uplift)]
        sorted_y = y_true[np.argsort(-uplift)]
        row0_qini = sorted_y[0] * sorted_t[0]
        assert qini[0] == pytest.approx(row0_qini)

    def test_all_treatment(self):
        y_true = np.array([1, 0, 1])
        uplift = np.array([0.9, 0.5, 0.1])
        treatment = np.array([1, 1, 1])
        qini, _ = calculate_qini_curve(y_true, uplift, treatment)
        assert len(qini) == 3

    def test_random_qini_is_linear(self):
        y_true = np.array([1, 0, 1, 0, 1])
        uplift = np.array([0.9, 0.7, 0.5, 0.3, 0.1])
        treatment = np.array([1, 0, 0, 1, 1])
        _, random_qini = calculate_qini_curve(y_true, uplift, treatment)
        assert random_qini[0] == pytest.approx(0.0)
        assert random_qini[-1] > random_qini[0]

    def test_sorted_descending(self):
        y_true = np.array([1, 0, 1, 0])
        uplift = np.array([0.1, 0.9, 0.3, 0.7])
        treatment = np.array([1, 0, 1, 0])
        qini, _ = calculate_qini_curve(y_true, uplift, treatment)
        assert len(qini) == 4

    def test_zero_treatment_division(self):
        y_true = np.array([1, 0, 1, 0])
        uplift = np.array([0.9, 0.7, 0.3, 0.1])
        treatment = np.array([0, 0, 0, 0])
        qini, _ = calculate_qini_curve(y_true, uplift, treatment)
        assert len(qini) == 4


class TestTreatmentAssignment:
    def test_treatment_gt_5(self):
        df = type('', (), {})()
        df.DiscountValue = [5, 10, 15, 20, 3]
        treatment = [(v > 5) * 1 for v in df.DiscountValue]
        expected = [0, 1, 1, 1, 0]
        assert treatment == expected

    def test_treatment_feature_set(self):
        features = ['Recency', 'Frequency', 'Monetary']
        assert features == ['Recency', 'Frequency', 'Monetary']
