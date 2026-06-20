import sys
import numpy as np
import pandas as pd
import pytest


class TestHeuristicUplift:
    def test_uplift_score_base_70_for_mid_recency(self):
        recency = np.array([6, 8, 5])
        freq = np.array([20, 10, 5])
        monetary = np.array([5000, 2000, 800])
        f_90, m_90 = 18.0, 4500.0
        f_score = np.clip(freq / f_90, 0, 1)
        m_score = np.clip(monetary / m_90, 0, 1)
        fm_avg = (f_score + m_score) / 2.0
        conditions = [
            (recency > 4) & (recency <= 10),
            (recency <= 4),
            (recency > 10)
        ]
        choices = [70 + (fm_avg * 30), 40 + (fm_avg * 30), 10 + (fm_avg * 30)]
        uplift = np.select(conditions, choices, default=0)
        assert all(u >= 70 for u in uplift)

    def test_uplift_score_base_40_for_low_recency(self):
        recency = np.array([1, 4, 3])
        freq = np.array([2, 1, 1])
        monetary = np.array([100, 50, 50])
        f_90, m_90 = 18.0, 4500.0
        f_score = np.clip(freq / f_90, 0, 1)
        m_score = np.clip(monetary / m_90, 0, 1)
        fm_avg = (f_score + m_score) / 2.0
        conditions = [
            (recency > 4) & (recency <= 10),
            (recency <= 4),
            (recency > 10)
        ]
        choices = [70 + (fm_avg * 30), 40 + (fm_avg * 30), 10 + (fm_avg * 30)]
        uplift = np.select(conditions, choices, default=0)
        assert all(40 <= u < 70 for u in uplift)
        assert all(u > 40 for u in uplift)

    def test_uplift_score_base_10_for_high_recency(self):
        recency = np.array([11, 100, 50])
        freq = np.array([2, 1, 1])
        monetary = np.array([100, 50, 50])
        f_90, m_90 = 18.0, 4500.0
        f_score = np.clip(freq / f_90, 0, 1)
        m_score = np.clip(monetary / m_90, 0, 1)
        fm_avg = (f_score + m_score) / 2.0
        conditions = [
            (recency > 4) & (recency <= 10),
            (recency <= 4),
            (recency > 10)
        ]
        choices = [70 + (fm_avg * 30), 40 + (fm_avg * 30), 10 + (fm_avg * 30)]
        uplift = np.select(conditions, choices, default=0)
        assert all(10 <= u < 40 for u in uplift)

    def test_fm_avg_bounded_0_to_1(self):
        f_score = np.array([0.0, 0.5, 1.0])
        m_score = np.array([0.0, 0.5, 1.0])
        fm_avg = (f_score + m_score) / 2.0
        assert np.all(fm_avg >= 0) and np.all(fm_avg <= 1)
        np.testing.assert_almost_equal(fm_avg, [0.0, 0.5, 1.0])

    def test_uplift_score_rounded(self):
        uplift = np.array([70.123, 40.456, 10.789])
        rounded = np.round(uplift, 2)
        assert rounded[0] == 70.12
        assert rounded[1] == 40.46
        assert rounded[2] == 10.79


class TestSegmentAssignment:
    def test_segment_persuadables(self):
        conditions = [
            (np.array([80]) >= 75),
            (np.array([80]) >= 50) & (np.array([80]) < 75),
            (np.array([80]) >= 25) & (np.array([80]) < 50),
            (np.array([80]) < 25)
        ]
        choices = ['Persuadables (Target)', 'Sure Things', 'Sleeping Dogs', 'Lost Causes']
        result = np.select(conditions, choices, default='Unknown')
        assert result[0] == 'Persuadables (Target)'

    def test_segment_sure_things(self):
        score = np.array([60])
        conditions = [
            (score >= 75),
            (score >= 50) & (score < 75),
            (score >= 25) & (score < 50),
            (score < 25)
        ]
        choices = ['Persuadables (Target)', 'Sure Things', 'Sleeping Dogs', 'Lost Causes']
        result = np.select(conditions, choices, default='Unknown')
        assert result[0] == 'Sure Things'

    def test_segment_sleeping_dogs(self):
        conditions = [
            (np.array([30]) >= 75),
            (np.array([30]) >= 50) & (np.array([30]) < 75),
            (np.array([30]) >= 25) & (np.array([30]) < 50),
            (np.array([30]) < 25)
        ]
        choices = ['Persuadables (Target)', 'Sure Things', 'Sleeping Dogs', 'Lost Causes']
        result = np.select(conditions, choices, default='Unknown')
        assert result[0] == 'Sleeping Dogs'

    def test_segment_lost_causes(self):
        conditions = [
            (np.array([10]) >= 75),
            (np.array([10]) >= 50) & (np.array([10]) < 75),
            (np.array([10]) >= 25) & (np.array([10]) < 50),
            (np.array([10]) < 25)
        ]
        choices = ['Persuadables (Target)', 'Sure Things', 'Sleeping Dogs', 'Lost Causes']
        result = np.select(conditions, choices, default='Unknown')
        assert result[0] == 'Lost Causes'

    def test_boundary_75_is_persuadable(self):
        assert np.select(
            [(np.array([75]) >= 75), (np.array([75]) >= 50), (np.array([75]) >= 25), (np.array([75]) < 25)],
            ['Persuadables (Target)', 'Sure Things', 'Sleeping Dogs', 'Lost Causes'], default='Unknown'
        )[0] == 'Persuadables (Target)'

    def test_boundary_50_is_sure_thing(self):
        score = np.array([50])
        assert np.select(
            [(score >= 75), (score >= 50) & (score < 75), (score >= 25) & (score < 50), (score < 25)],
            ['Persuadables (Target)', 'Sure Things', 'Sleeping Dogs', 'Lost Causes'], default='Unknown'
        )[0] == 'Sure Things'

    def test_boundary_25_is_sleeping_dog(self):
        score = np.array([25])
        assert np.select(
            [(score >= 75), (score >= 50) & (score < 75), (score >= 25) & (score < 50), (score < 25)],
            ['Persuadables (Target)', 'Sure Things', 'Sleeping Dogs', 'Lost Causes'], default='Unknown'
        )[0] == 'Sleeping Dogs'


class TestDataSelection:
    def test_output_columns_exist(self):
        output_cols = ['CustomerID', 'Recency', 'Frequency', 'Monetary',
                       'Is_Redeemer', 'TotalReturns', 'Uplift_Score', 'Segment_Label']
        assert len(output_cols) == 8
        assert 'Uplift_Score' in output_cols
        assert 'Segment_Label' in output_cols

    def test_quantile_capping(self):
        data = np.array([1, 2, 3, 4, 5, 100, 200])
        q90 = np.quantile(data, 0.9)
        assert q90 > 0
        capped = np.clip(data / q90, 0, 1)
        assert capped[-1] == 1.0
        assert capped[-2] < 1.0
