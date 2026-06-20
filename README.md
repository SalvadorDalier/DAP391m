# DAP391m - Online Retail II Uplift Modeling


Uplift modeling project using a T-Learner (XGBoost) on the UCI Online Retail II dataset. Predicts customer sensitivity to coupons to maximize marketing ROI by targeting only Persuadable customers.

---

## Data Source

D. Chen. "Online Retail II," UCI Machine Learning Repository, 2012.
https://doi.org/10.24432/C5CG6D

Download `online_retail_09_10.csv` from Kaggle and place it at:
```
data/raw/online_retail_09_10.csv
```

---

## Setup

```bash
# Clone
git clone https://github.com/SalvadorDalier/DAP391m.git
cd DAP391m

# Virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Dependencies
pip install -r requirements.txt
```

---

## Project Structure

```
data/
  raw/              - input CSV (download manually)
  processed/        - pipeline output CSVs
  external/         - external reference data
models/             - trained .pkl files (baseline + uplift)
notebooks/          - Jupyter notebooks (placeholder)
src/
  app.py            - Streamlit what-if dashboard
  config.py         - centralized path/config/params
  pipeline.py       - full pipeline orchestration
  api/server.py     - Flask REST API
  preprocessing/
    ingest.py       - load, clean, validate raw data
    features.py     - RFM calculation + coupon simulation
    split.py        - train/test split with stratification
  models/
    train.py        - LogisticRegression baseline + XGBoost T-Learner
    evaluate.py     - Qini curve, AUUC, cost-benefit analysis
    predict.py      - CATE prediction + segment assignment
    viz.py          - plotting utilities
tests/              - 87 pytest tests
reports/
  figures/          - eda/ and evaluation/ charts
  latex/            - research paper (LaTeX)
  slide/            - presentation
  proposals/        - research proposals
  docs/             - documentation, user guide, step reports
  audit_log/        - AI audit log scripts
```

---

## Pipeline

Run the full pipeline end-to-end:

```bash
python src/pipeline.py
```

Steps:
1. **Ingest** - load CSV, drop missing CustomerID, cancelations, negative values, cap outliers at P99
2. **RFM** - compute Recency/Frequency/Monetary, assign RFM quintiles, segment customers, simulate coupons (RandomState 42)
3. **Split** - rename IsRedeemed to Is_Redeemer, generate Treatment column (DiscountValue > 5), 80/20 stratified split
4. **Train** - LogisticRegression baseline + XGBoost T-Learner (control + treatment models)
5. **Evaluate** - calculate Qini curve, AUUC, Qini gain, cost-benefit analysis by decile
6. **Predict** - predict CATE for all customers, map to segments (Persuadables, Sure Things, Sleeping Dogs, Lost Causes)

Results are saved to `data/processed/` and `models/`.

---

## Dashboard (Streamlit)

```bash
streamlit run src/app.py
```

Three tabs:
- **What-If Targeting** - adjust coupon cost and margin sliders, see dynamic target list with expected profit
- **Executive Summary** - compare mass mailing vs AI-targeted ROI
- **Customer Lookup** - search by Customer ID for CATE, segment, recommendation
