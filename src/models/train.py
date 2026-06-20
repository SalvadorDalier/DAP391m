import numpy as np
import pandas as pd
import pickle
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from .. import config


def train_baseline(X_train: pd.DataFrame, y_train: pd.Series) -> LogisticRegression:
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    return model


def train_t_learner(X_train: pd.DataFrame, y_train: pd.Series, t_train: pd.Series) -> dict:
    mask_c = (t_train == 0)
    mask_t = (t_train == 1)
    xgb_control = xgb.XGBClassifier(**config.XGB_PARAMS)
    xgb_treatment = xgb.XGBClassifier(**config.XGB_PARAMS)
    xgb_control.fit(X_train[mask_c], y_train[mask_c])
    xgb_treatment.fit(X_train[mask_t], y_train[mask_t])
    return {'control_model': xgb_control, 'treatment_model': xgb_treatment}


def train_pipeline(train_df: pd.DataFrame) -> dict:
    X_train = train_df[config.FEATURES]
    y_train = train_df[config.TARGET]
    t_train = train_df[config.TREATMENT]
    X_train_base = train_df[config.FEATURES_BASELINE]
    baseline = train_baseline(X_train_base, y_train)
    baseline_acc = accuracy_score(y_train, baseline.predict(X_train_base))
    uplift_models = train_t_learner(X_train, y_train, t_train)
    return {
        'baseline': baseline,
        'baseline_accuracy': baseline_acc,
        'uplift_models': uplift_models,
    }


def main():
    import pickle
    train_df = pd.read_csv(config.TRAIN_DATA_FILE)
    result = train_pipeline(train_df)
    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.BASELINE_MODEL_FILE, 'wb') as f:
        pickle.dump(result['baseline'], f)
    with open(config.UPLIFT_MODEL_FILE, 'wb') as f:
        pickle.dump(result['uplift_models'], f)
    print(f"Baseline accuracy: {result['baseline_accuracy']:.4f}")
    print(f"Models saved to {config.MODEL_DIR}")


if __name__ == '__main__':
    main()
