# DAP391m - Online Retail II Uplift Modeling

Uplift modeling project using T-Learner XGBoost on the UCI Online Retail II dataset. Predicts customer sensitivity to coupons to maximize marketing ROI.

## Data Source

D. Chen. "Online Retail II," UCI Machine Learning Repository, 2012.
https://doi.org/10.24432/C5CG6D

Place `online_retail_09_10.csv` in `data/raw/` before running.

## Structure

```
data/              - raw/processed/external data
models/            - trained .pkl files
notebooks/         - Jupyter notebooks
src/
  app.py           - Streamlit dashboard
  config.py        - centralized config
  pipeline.py      - orchestration (ingest -> rfm -> split -> train -> evaluate -> predict)
  api/server.py    - Flask REST API
  preprocessing/   - ingest, features (RFM), split
  models/          - train, evaluate, predict, viz
tests/             - 87 pytest tests
reports/           - figures, latex, slide, proposals, docs, audit_log
```

## Usage

```bash
# pipeline
python src/pipeline.py

# dashboard
streamlit run src/app.py

# API
python src/api/server.py

# tests
pytest tests/
```

## Requirements

- Python 3.10+
- packages in requirements.txt
