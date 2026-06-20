import pandas as pd
from sklearn.model_selection import train_test_split
from .. import config


def prepare_for_split(rfm_df: pd.DataFrame) -> pd.DataFrame:
    df = rfm_df.copy()
    if 'IsRedeemed' in df.columns:
        df.rename(columns={'IsRedeemed': 'Is_Redeemer'}, inplace=True)
    if 'TotalReturns' not in df.columns:
        df['TotalReturns'] = 0.0
    if config.TREATMENT not in df.columns and 'DiscountValue' in df.columns:
        df[config.TREATMENT] = (df['DiscountValue'] > 5).astype(int)
    return df


def split_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df, test_df = train_test_split(
        df,
        test_size=config.SPLIT_RATIO,
        random_state=config.SPLIT_RANDOM_STATE,
        stratify=df['Is_Redeemer']
    )
    return train_df, test_df


def build_split_pipeline(rfm_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = prepare_for_split(rfm_df)
    return split_data(df)


def main():
    rfm_df = pd.read_csv(config.RFM_FILE)
    train_df, test_df = build_split_pipeline(rfm_df)
    train_df.to_csv(config.TRAIN_DATA_FILE, index=False)
    test_df.to_csv(config.TEST_DATA_FILE, index=False)
    print(f"Train: {len(train_df)} rows, Test: {len(test_df)} rows")


if __name__ == '__main__':
    main()
