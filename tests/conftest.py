from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import pytest


@pytest.fixture
def sample_rfm_df():
    return pd.DataFrame({
        'CustomerID': [10001, 10002, 10003, 10004, 10005],
        'Recency': [10, 30, 200, 500, 5],
        'Frequency': [20, 8, 3, 1, 15],
        'Monetary': [8000.0, 2000.0, 500.0, 100.0, 6000.0],
        'Is_Redeemer': [1, 1, 0, 0, 1],
        'DiscountValue': [10, 5, 20, 15, 10],
        'CouponType': ['PERCENTAGE', 'FIXED', 'BOGO', 'PERCENTAGE', 'FIXED'],
        'TotalReturns': [0.0, 0.0, 0.0, 0.0, 0.0],
    })


@pytest.fixture
def sample_uplift_df():
    np.random.seed(42)
    n = 50
    return pd.DataFrame({
        'CustomerID': np.arange(10001, 10001 + n),
        'Recency': np.random.randint(1, 600, n),
        'Frequency': np.random.randint(1, 40, n),
        'Monetary': np.random.uniform(100, 10000, n),
        'Is_Redeemer': np.random.choice([0, 1], n, p=[0.6, 0.4]),
        'DiscountValue': np.random.choice([5, 10, 15, 20], n),
        'CouponType': np.random.choice(['PERCENTAGE', 'FIXED', 'BOGO'], n),
    })


@pytest.fixture
def sample_cate_df():
    return pd.DataFrame({
        'CustomerID': [10001, 10002, 10003, 10004],
        'Recency': [10, 30, 200, 500],
        'Frequency': [20, 8, 3, 1],
        'Monetary': [8000.0, 2000.0, 500.0, 100.0],
        'CATE': [0.15, 0.05, -0.02, -0.10],
        'prob_c': [0.3, 0.6, 0.4, 0.2],
        'prob_t': [0.45, 0.65, 0.38, 0.10],
    })
