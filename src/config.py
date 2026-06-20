from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_EXTERNAL = PROJECT_ROOT / "data" / "external"

RAW_DATA_FILE = DATA_RAW / "online_retail_09_10.csv"
RFM_FILE = DATA_PROCESSED / "customer_rfm.csv"
PREDICTIONS_FILE = DATA_PROCESSED / "predictions.csv"
TRAIN_DATA_FILE = DATA_PROCESSED / "train_data.csv"
TEST_DATA_FILE = DATA_PROCESSED / "test_data.csv"

MODEL_DIR = PROJECT_ROOT / "models"
BASELINE_MODEL_FILE = MODEL_DIR / "baseline_logistic.pkl"
UPLIFT_MODEL_FILE = MODEL_DIR / "uplift_xgboost_manual.pkl"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

FEATURES = ['Recency', 'Frequency', 'Monetary']
FEATURES_BASELINE = ['Recency', 'Frequency', 'Monetary', 'DiscountValue']
TARGET = 'Is_Redeemer'
TREATMENT = 'Treatment'

RFM_QUINTILES = 5

COUPON_SEED = 42
COUPON_TYPES = ['PERCENTAGE', 'FIXED_AMOUNT', 'BOGO']
COUPON_DISCOUNT_VALUES = [10, 20, 5, 15]
COUPON_REDEEM_PROB = 0.3

SPLIT_RATIO = 0.2
SPLIT_RANDOM_STATE = 42

XGB_PARAMS = {
    'n_estimators': 100,
    'max_depth': 2,
    'learning_rate': 0.05,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'eval_metric': 'logloss',
    'random_state': 42,
}

COUPON_COST = 5.0
MARGIN = 0.3

API_PORT = 5000
API_DEBUG = True

SQL_SERVER = 'localhost'
SQL_DATABASE = 'Project11DB'
SQL_DRIVER = 'ODBC+Driver+18+for+SQL+Server'
