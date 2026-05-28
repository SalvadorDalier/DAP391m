import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_curve, auc

def calculate_qini_curve(y_true, uplift, treatment):
    df = pd.DataFrame({'y': y_true, 'uplift': uplift, 't': treatment})
    df = df.sort_values(by='uplift', ascending=False).reset_index(drop=True)
    df['n_t'] = df['t'].cumsum()
    df['n_c'] = (~df['t'].astype(bool)).cumsum()
    df['y_t'] = (df['y'] * df['t']).cumsum()
    df['y_c'] = (df['y'] * (~df['t'].astype(bool))).cumsum()
    df['qini'] = df['y_t'] - df['y_c'] * (df['n_t'] / df['n_c'].replace(0, 1))
    
    total_y_t = df['y_t'].iloc[-1]
    total_y_c = df['y_c'].iloc[-1]
    total_n_t = df['n_t'].iloc[-1]
    total_n_c = df['n_c'].iloc[-1]
    
    max_qini = total_y_t - total_y_c * (total_n_t / total_n_c)
    df['random_qini'] = np.linspace(0, max_qini, len(df))
    return df['qini'], df['random_qini']

def main():
    print("=== Bước 5: Xây dựng Mô hình Dự đoán Uplift (Manual T-Learner) ===")
    
    base_dir = r"C:\Users\Lenovo\Desktop\DAP391_project"
    visual_dir = os.path.join(base_dir, "05_visuals", "evaluation")
    os.makedirs(visual_dir, exist_ok=True)
    
    print("Đang tải dữ liệu...")
    train_path = os.path.join(base_dir, "01_data", "train_test", "train_data.csv")
    test_path = os.path.join(base_dir, "01_data", "train_test", "test_data.csv")
    rfm_path = os.path.join(base_dir, "01_data", "processed", "customer_rfm.csv")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    rfm_df = pd.read_csv(rfm_path)
    
    if 'DiscountValue' not in train_df.columns:
        rfm_cols = ['CustomerID', 'CouponType', 'DiscountValue']
        train_merged = train_df.merge(rfm_df[rfm_cols], on='CustomerID', how='inner')
        test_merged = test_df.merge(rfm_df[rfm_cols], on='CustomerID', how='inner')
    else:
        train_merged = train_df
        test_merged = test_df
    
    train_merged['Treatment'] = (train_merged['DiscountValue'] > 5).astype(int)
    test_merged['Treatment'] = (test_merged['DiscountValue'] > 5).astype(int)
    
    features = ['Recency', 'Frequency', 'Monetary']
    X_train = train_merged[features]
    y_train = train_merged['Is_Redeemer']
    t_train = train_merged['Treatment']
    
    X_test = test_merged[features]
    y_test = test_merged['Is_Redeemer']
    t_test = test_merged['Treatment']
    
    # --- 1. Logistic Regression Baseline ---
    print("\nĐang huấn luyện Baseline Model (Logistic Regression)...")
    features_baseline = ['Recency', 'Frequency', 'Monetary', 'DiscountValue']
    X_train_base = train_merged[features_baseline]
    X_test_base = test_merged[features_baseline]
    
    baseline_model = LogisticRegression(max_iter=1000)
    baseline_model.fit(X_train_base, y_train)
    
    pred_base_class = baseline_model.predict(X_test_base)
    pred_base_prob = baseline_model.predict_proba(X_test_base)[:, 1]
    print(f"Độ chính xác (Accuracy) của Baseline Model trên tập Test: {accuracy_score(y_test, pred_base_class):.4f}")
    
    # VẼ CHART CHO LOGISTIC REGRESSION (ROC CURVE)
    fpr, tpr, _ = roc_curve(y_test, pred_base_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.title('Baseline Logistic Regression ROC Curve')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc="lower right")
    lr_chart_path = os.path.join(visual_dir, 'logistic_regression_roc.png')
    plt.savefig(lr_chart_path)
    plt.close()
    print(f"Đã lưu biểu đồ ROC tại: {lr_chart_path}")
    
    model_dir = os.path.join(base_dir, "04_models", "saved")
    os.makedirs(model_dir, exist_ok=True)
    with open(os.path.join(model_dir, "baseline_logistic.pkl"), "wb") as f:
        pickle.dump(baseline_model, f)
        
    # --- 2. XGBoost T-Learner ---
    print("\nĐang huấn luyện Uplift Model (XGBoost T-Learner)...")
    
    xgb_control = xgb.XGBClassifier(random_state=42, n_estimators=100, max_depth=3, eval_metric='logloss')
    xgb_treatment = xgb.XGBClassifier(random_state=42, n_estimators=100, max_depth=3, eval_metric='logloss')
    
    mask_c_train = (t_train == 0)
    mask_t_train = (t_train == 1)
    mask_c_test = (t_test == 0)
    mask_t_test = (t_test == 1)
    
    eval_set_c = [(X_train[mask_c_train], y_train[mask_c_train]), (X_test[mask_c_test], y_test[mask_c_test])]
    eval_set_t = [(X_train[mask_t_train], y_train[mask_t_train]), (X_test[mask_t_test], y_test[mask_t_test])]
    
    # Huấn luyện và thu thập logloss để vẽ Loss Curve
    xgb_control.fit(X_train[mask_c_train], y_train[mask_c_train], eval_set=eval_set_c, verbose=False)
    xgb_treatment.fit(X_train[mask_t_train], y_train[mask_t_train], eval_set=eval_set_t, verbose=False)
    
    # VẼ LOSS CURVE CHO XGBOOST
    results_c = xgb_control.evals_result()
    results_t = xgb_treatment.evals_result()
    
    plt.figure(figsize=(14, 5))
    plt.subplot(1, 2, 1)
    plt.plot(results_c['validation_0']['logloss'], label='Train')
    plt.plot(results_c['validation_1']['logloss'], label='Test')
    plt.title('Control Model (T=0) - Log Loss Curve')
    plt.xlabel('Epochs (Trees)')
    plt.ylabel('Log Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(results_t['validation_0']['logloss'], label='Train')
    plt.plot(results_t['validation_1']['logloss'], label='Test')
    plt.title('Treatment Model (T=1) - Log Loss Curve')
    plt.xlabel('Epochs (Trees)')
    plt.ylabel('Log Loss')
    plt.legend()
    
    loss_curve_path = os.path.join(visual_dir, 'xgboost_loss_curve.png')
    plt.tight_layout()
    plt.savefig(loss_curve_path)
    plt.close()
    print(f"Đã lưu biểu đồ Loss Curve tại: {loss_curve_path}")
    
    prob_c = xgb_control.predict_proba(X_test)[:, 1]
    prob_t = xgb_treatment.predict_proba(X_test)[:, 1]
    uplift_preds = prob_t - prob_c
    
    uplift_model_dict = {
        'control_model': xgb_control,
        'treatment_model': xgb_treatment
    }
    with open(os.path.join(model_dir, "uplift_xgboost_manual.pkl"), "wb") as f:
        pickle.dump(uplift_model_dict, f)
        
    print("Huấn luyện hoàn tất! Tiến hành đánh giá QINI & Feature Importance...")
    
    # --- 3. Đánh giá QINI ---
    qini, random_qini = calculate_qini_curve(y_test.values, uplift_preds, t_test.values)
    auuc_score = np.trapezoid(qini) / len(qini)
    random_auuc = np.trapezoid(random_qini) / len(random_qini)
    
    print(f"\n--- ĐÁNH GIÁ MÔ HÌNH UPLIFT ---")
    print(f"AUUC (Area Under Uplift Curve): {auuc_score:.4f}")
    print(f"Random AUUC: {random_auuc:.4f}")
    print(f"QINI Gain (AUUC - Random AUUC): {auuc_score - random_auuc:.4f}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(qini)), qini, label='XGBoost T-Learner Uplift')
    plt.plot(range(len(random_qini)), random_qini, label='Random', linestyle='--')
    plt.title('QINI Curve Comparison')
    plt.xlabel('Number of Customers Targeted')
    plt.ylabel('Incremental Number of Successes (Qini)')
    plt.legend()
    qini_path = os.path.join(visual_dir, "qini_curve_evaluation.png")
    plt.savefig(qini_path)
    plt.close()
    
    # --- 4. Feature Importance ---
    imp_c = xgb_control.feature_importances_
    imp_t = xgb_treatment.feature_importances_
    imp_avg = (imp_c + imp_t) / 2.0
    
    plt.figure(figsize=(8, 5))
    pd.Series(imp_avg, index=features).sort_values().plot(kind='barh', color='teal', edgecolor='black')
    plt.title('Uplift Model Feature Importance')
    plt.xlabel('Relative Importance')
    
    # Ghi chú giá trị trên thanh
    for index, value in enumerate(pd.Series(imp_avg, index=features).sort_values()):
        plt.text(value, index, f" {value:.4f}")
        
    feat_imp_path = os.path.join(visual_dir, "feature_importance_uplift.png")
    plt.tight_layout()
    plt.savefig(feat_imp_path)
    plt.close()
    print(f"Đã lưu biểu đồ Feature Importance mới tại: {feat_imp_path}")
        
    print("\nHoàn thành!")

if __name__ == "__main__":
    main()
