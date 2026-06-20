import numpy as np
import pytest
from src.models.predict import map_cate_to_score_and_segment


class TestMapCateToSegment:
    def test_persuadable_positive_cate(self):
        score, segment = map_cate_to_score_and_segment(0.15, 0.3, 0.2, 0.02, -0.15)
        assert segment == 'Persuadables (Target)'
        assert 75 <= score <= 100

    def test_persuadable_high_cate(self):
        score, segment = map_cate_to_score_and_segment(0.2, 0.3, 0.2, 0.02, -0.15)
        assert segment == 'Persuadables (Target)'
        assert score == pytest.approx(100.0)

    def test_sleeping_dog_negative_cate(self):
        score, segment = map_cate_to_score_and_segment(-0.10, 0.4, 0.2, 0.02, -0.15)
        assert segment == 'Sleeping Dogs'
        assert 25 <= score <= 50

    def test_sure_thing_low_cate_high_prob(self):
        score, segment = map_cate_to_score_and_segment(0.005, 0.7, 0.2, 0.02, -0.15)
        assert segment == 'Sure Things'
        assert 50 <= score <= 75

    def test_lost_cause_low_cate_low_prob(self):
        score, segment = map_cate_to_score_and_segment(0.005, 0.3, 0.2, 0.02, -0.15)
        assert segment == 'Lost Causes'
        assert 0 <= score <= 25

    def test_edge_cate_zero(self):
        score, segment = map_cate_to_score_and_segment(0.0, 0.6, 0.2, 0.02, -0.15)
        assert segment in ('Sure Things', 'Lost Causes')

    def test_boundary_positive_cate(self):
        score, segment = map_cate_to_score_and_segment(0.011, 0.3, 0.2, 0.02, -0.15)
        assert segment == 'Persuadables (Target)'

    def test_boundary_negative_cate(self):
        score, segment = map_cate_to_score_and_segment(-0.011, 0.3, 0.2, 0.02, -0.15)
        assert segment == 'Sleeping Dogs'
