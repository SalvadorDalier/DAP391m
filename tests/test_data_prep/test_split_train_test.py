import pandas as pd
import numpy as np
import pytest


class TestColumnMapping:
    def test_isredeemer_rename(self):
        df = pd.DataFrame({
            'CustomerID': [1, 2],
            'Recency': [10, 20],
            'Frequency': [5, 3],
            'Monetary': [100, 200],
            'IsRedeemed': [1, 0],
        })
        if 'IsRedeemed' in df.columns:
            df.rename(columns={'IsRedeemed': 'Is_Redeemer'}, inplace=True)
        assert 'Is_Redeemer' in df.columns
        assert 'IsRedeemed' not in df.columns

    def test_totalreturns_added(self):
        df = pd.DataFrame({
            'CustomerID': [1, 2],
            'Recency': [10, 20],
            'Frequency': [5, 3],
            'Monetary': [100, 200],
            'Is_Redeemer': [1, 0],
        })
        if 'TotalReturns' not in df.columns:
            df['TotalReturns'] = 0.0
        assert 'TotalReturns' in df.columns
        assert (df['TotalReturns'] == 0.0).all()


class TestSplitBehavior:
    def test_80_20_split_ratio(self):
        np.random.seed(42)
        df = pd.DataFrame({
            'CustomerID': range(100),
            'Recency': np.random.randint(1, 600, 100),
            'Frequency': np.random.randint(1, 40, 100),
            'Monetary': np.random.uniform(100, 10000, 100),
            'Is_Redeemer': np.random.choice([0, 1], 100, p=[0.6, 0.4]),
            'TotalReturns': [0.0] * 100,
        })
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(
            df, test_size=0.2, random_state=42, stratify=df['Is_Redeemer']
        )
        assert len(train_df) == 80
        assert len(test_df) == 20

    def test_columns_preserved_after_split(self):
        np.random.seed(42)
        df = pd.DataFrame({
            'CustomerID': range(100),
            'Recency': np.random.randint(1, 600, 100),
            'Frequency': np.random.randint(1, 40, 100),
            'Monetary': np.random.uniform(100, 10000, 100),
            'Is_Redeemer': np.random.choice([0, 1], 100, p=[0.6, 0.4]),
            'TotalReturns': [0.0] * 100,
        })
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['Is_Redeemer'])
        assert list(train_df.columns) == list(df.columns)
        assert list(test_df.columns) == list(df.columns)

    def test_stratified_split_preserves_ratio(self):
        np.random.seed(42)
        df = pd.DataFrame({
            'CustomerID': range(500),
            'Recency': np.random.randint(1, 600, 500),
            'Frequency': np.random.randint(1, 40, 500),
            'Monetary': np.random.uniform(100, 10000, 500),
            'Is_Redeemer': np.random.choice([0, 1], 500, p=[0.7, 0.3]),
            'TotalReturns': [0.0] * 500,
        })
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['Is_Redeemer'])
        orig_ratio = df['Is_Redeemer'].mean()
        train_ratio = train_df['Is_Redeemer'].mean()
        test_ratio = test_df['Is_Redeemer'].mean()
        assert abs(orig_ratio - train_ratio) < 0.05
        assert abs(orig_ratio - test_ratio) < 0.05

    def test_no_overlap_between_train_test(self):
        np.random.seed(42)
        df = pd.DataFrame({
            'CustomerID': range(500),
            'Recency': np.random.randint(1, 600, 500),
            'Frequency': np.random.randint(1, 40, 500),
            'Monetary': np.random.uniform(100, 10000, 500),
            'Is_Redeemer': np.random.choice([0, 1], 500, p=[0.7, 0.3]),
            'TotalReturns': [0.0] * 500,
        })
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['Is_Redeemer'])
        assert set(train_df['CustomerID']).isdisjoint(set(test_df['CustomerID']))
