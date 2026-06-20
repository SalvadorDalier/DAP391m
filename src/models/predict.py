import pandas as pd
import numpy as np
from .. import config


def map_cate_to_score_and_segment(
    cate: float, prob_c: float, max_cate: float,
    min_cate_positive: float, min_cate_negative: float
) -> tuple[float, str]:
    if cate > 0.01:
        range_cate = max_cate - 0.01 if max_cate > 0.01 else 0.01
        score = 75 + ((cate - 0.01) / range_cate) * 25
        score = min(100.0, score)
        return score, 'Persuadables (Target)'
    elif cate < -0.01:
        range_cate = -0.01 - min_cate_negative if min_cate_negative < -0.01 else 0.01
        val = ((cate - min_cate_negative) / range_cate) * 24
        score = 25 + max(0, min(24, val))
        return score, 'Sleeping Dogs'
    else:
        if prob_c >= 0.5:
            score = 50 + ((prob_c - 0.5) / 0.5) * 24
            return score, 'Sure Things'
        else:
            score = (prob_c / 0.5) * 24
            return score, 'Lost Causes'


def predict_cate(rfm_df: pd.DataFrame, uplift_models: dict) -> pd.DataFrame:
    X = rfm_df[config.FEATURES]
    prob_c = uplift_models['control_model'].predict_proba(X)[:, 1]
    prob_t = uplift_models['treatment_model'].predict_proba(X)[:, 1]
    cate = prob_t - prob_c
    result = rfm_df.copy()
    result['prob_c'] = prob_c
    result['prob_t'] = prob_t
    result['CATE'] = cate
    return result


def assign_segments(result: pd.DataFrame) -> pd.DataFrame:
    max_cate = result['CATE'].max()
    pos = result[result['CATE'] > 0.01]
    min_cate_positive = pos['CATE'].min() if not pos.empty else 0.01
    min_cate_negative = result['CATE'].min()
    scores, segments = [], []
    for _, row in result.iterrows():
        s, seg = map_cate_to_score_and_segment(
            row['CATE'], row['prob_c'],
            max_cate, min_cate_positive, min_cate_negative
        )
        scores.append(s)
        segments.append(seg)
    result['Uplift_Score'] = np.round(scores, 2)
    result['Segment_Label'] = segments
    return result


def predict_pipeline(rfm_df: pd.DataFrame, uplift_models: dict) -> pd.DataFrame:
    result = predict_cate(rfm_df, uplift_models)
    result = assign_segments(result)
    return result


def main():
    import pickle
    test_df = pd.read_csv(config.TEST_DATA_FILE)
    rfm_df = pd.read_csv(config.RFM_FILE)
    with open(config.UPLIFT_MODEL_FILE, 'rb') as f:
        uplift_models = pickle.load(f)
    result = predict_pipeline(rfm_df, uplift_models)
    result.to_csv(config.PREDICTIONS_FILE, index=False)
    print(f"Predictions saved: {len(result)} customers")


if __name__ == '__main__':
    main()
