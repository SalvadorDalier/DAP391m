import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


sns.set(style="whitegrid")
plt.rcParams['figure.titlesize'] = 16


def plot_uplift_histogram(uplift_preds: np.ndarray, save_path: str) -> None:
    plt.figure(figsize=(8, 5))
    sns.histplot(uplift_preds, bins=30, kde=True, color='teal')
    plt.axvline(0, color='red', linestyle='--')
    plt.title('Uplift Histogram (Predicted Lift Distribution)')
    plt.xlabel('Uplift Score')
    plt.ylabel('Customer Count')
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_rfm_comparison(df: pd.DataFrame, save_path: str) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    cols = ['Recency', 'Frequency', 'Monetary']
    titles = {'Recency': 'Recency', 'Frequency': 'Frequency', 'Monetary': 'Monetary'}
    for i, col in enumerate(cols):
        sns.boxplot(x='Is_Redeemer', y=col, data=df, hue='Is_Redeemer',
                    palette='Set2', legend=False, ax=axes[i])
        axes[i].set_title(titles[col])
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_qini_curve(qini: np.ndarray, random_qini: np.ndarray, save_path: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(qini)), qini, label='XGBoost T-Learner Uplift')
    plt.plot(range(len(random_qini)), random_qini, label='Random', linestyle='--')
    plt.title('QINI Curve Comparison')
    plt.xlabel('Number of Customers Targeted')
    plt.ylabel('Incremental Number of Successes (Qini)')
    plt.legend()
    plt.savefig(save_path)
    plt.close()


def plot_roc_curve(fpr: np.ndarray, tpr: np.ndarray, roc_auc: float, save_path: str) -> None:
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.title('ROC Curve')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc="lower right")
    plt.savefig(save_path)
    plt.close()


def plot_loss_curve(results_c: dict, results_t: dict, save_path: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(results_c['validation_0']['logloss'], label='Train')
    axes[0].plot(results_c['validation_1']['logloss'], label='Test')
    axes[0].set_title('Control Model (T=0) - Log Loss')
    axes[0].set_xlabel('Epochs')
    axes[0].set_ylabel('Log Loss')
    axes[0].legend()
    axes[1].plot(results_t['validation_0']['logloss'], label='Train')
    axes[1].plot(results_t['validation_1']['logloss'], label='Test')
    axes[1].set_title('Treatment Model (T=1) - Log Loss')
    axes[1].set_xlabel('Epochs')
    axes[1].set_ylabel('Log Loss')
    axes[1].legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_feature_importance(importances: np.ndarray, feature_names: list, save_path: str) -> None:
    plt.figure(figsize=(8, 5))
    pd.Series(importances, index=feature_names).sort_values().plot(
        kind='barh', color='teal', edgecolor='black')
    plt.title('Uplift Model Feature Importance')
    plt.xlabel('Relative Importance')
    for idx, val in enumerate(pd.Series(importances, index=feature_names).sort_values()):
        plt.text(val, idx, f" {val:.4f}")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_cost_benefit(cb_table: pd.DataFrame, save_path: str) -> None:
    plt.figure(figsize=(10, 6))
    sns.barplot(x=cb_table.index, y=cb_table['net_profit'], hue=cb_table.index,
                palette='RdYlGn', legend=False)
    plt.title('Net Profit by Uplift Decile')
    plt.xlabel('Decile (1 = Highest, 10 = Lowest)')
    plt.ylabel('Expected Net Profit ($)')
    plt.axhline(0, color='black', linewidth=1)
    plt.savefig(save_path)
    plt.close()


def plot_uplift_roc(df_test: pd.DataFrame, save_path: str) -> None:
    from sklearn.metrics import roc_curve, auc
    df_test['true_uplift_proxy'] = (df_test['Is_Redeemer'] == df_test['Treatment']).astype(int)
    fpr, tpr, _ = roc_curve(df_test['true_uplift_proxy'], df_test['uplift_score'])
    roc_auc = auc(fpr, tpr)
    plot_roc_curve(fpr, tpr, roc_auc, save_path)
