import numpy as np
import pandas as pd
from .. import config


def calculate_qini_curve(y_true: np.ndarray, uplift: np.ndarray, treatment: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    df = pd.DataFrame({'y': y_true, 'uplift': uplift, 't': treatment})
    df = df.sort_values(by='uplift', ascending=False).reset_index(drop=True)
    df['n_t'] = df['t'].cumsum()
    df['n_c'] = (~df['t'].astype(bool)).cumsum()
    df['y_t'] = (df['y'] * df['t']).cumsum()
    df['y_c'] = (df['y'] * (~df['t'].astype(bool))).cumsum()
    total_n_t = df['n_t'].iloc[-1]
    total_n_c = df['n_c'].iloc[-1]
    total_y_t = df['y_t'].iloc[-1]
    total_y_c = df['y_c'].iloc[-1]
    df['qini'] = df['y_t'] - df['y_c'] * (total_n_t / total_n_c)
    max_qini = total_y_t - total_y_c * (total_n_t / total_n_c)
    df['random_qini'] = np.linspace(0, max_qini, len(df))
    return df['qini'].values, df['random_qini'].values


def calculate_auuc(qini: np.ndarray) -> float:
    return float(np.trapezoid(qini) / len(qini))


def evaluate_pipeline(test_df: pd.DataFrame, uplift_models: dict) -> dict:
    X_test = test_df[config.FEATURES]
    y_test = test_df[config.TARGET].values
    t_test = test_df[config.TREATMENT].values
    prob_c = uplift_models['control_model'].predict_proba(X_test)[:, 1]
    prob_t = uplift_models['treatment_model'].predict_proba(X_test)[:, 1]
    uplift_preds = prob_t - prob_c
    qini, random_qini = calculate_qini_curve(y_test, uplift_preds, t_test)
    auuc = calculate_auuc(qini)
    random_auuc = calculate_auuc(random_qini)
    return {
        'uplift_preds': uplift_preds,
        'prob_c': prob_c,
        'prob_t': prob_t,
        'qini': qini,
        'random_qini': random_qini,
        'auuc': auuc,
        'random_auuc': random_auuc,
        'qini_gain': auuc - random_auuc,
    }


def cost_benefit_analysis(uplift_preds: np.ndarray, monetary: np.ndarray, n_deciles: int = 10) -> pd.DataFrame:
    df = pd.DataFrame({'uplift': uplift_preds, 'Monetary': monetary})
    df['decile'] = pd.qcut(df['uplift'], n_deciles, labels=np.arange(n_deciles, 0, -1))
    cb = df.groupby('decile', observed=True).agg(
        count=('uplift', 'count'),
        uplift_mean=('uplift', 'mean'),
        monetary_mean=('Monetary', 'mean')
    )
    cb['total_cost'] = cb['count'] * config.COUPON_COST
    cb['uplift_revenue'] = cb['count'] * cb['uplift_mean']
    cb['net_profit'] = (cb['uplift_revenue'] * config.MARGIN) - cb['total_cost']
    cb['roi_pct'] = (cb['net_profit'] / cb['total_cost']) * 100
    return cb


def main():
    import pickle
    test_df = pd.read_csv(config.TEST_DATA_FILE)
    train_df = pd.read_csv(config.TRAIN_DATA_FILE)
    t_train = train_df[config.TREATMENT]
    X_train = train_df[config.FEATURES]
    y_train = train_df[config.TARGET]
    from .train import train_t_learner
    uplift_models = train_t_learner(X_train, y_train, t_train)
    ev = evaluate_pipeline(test_df, uplift_models)
    print(f"AUUC: {ev['auuc']:.4f}")
    print(f"Random AUUC: {ev['random_auuc']:.4f}")
    print(f"Qini Gain: {ev['qini_gain']:.4f}")


if __name__ == '__main__':
    main()
