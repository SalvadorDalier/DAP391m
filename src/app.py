import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import pickle

ROOT = Path(__file__).resolve().parent.parent
RFM_FILE = ROOT / "data" / "processed" / "customer_rfm.csv"
UPLIFT_MODEL_FILE = ROOT / "models" / "uplift_xgboost_manual.pkl"
FEATURES = ['Recency', 'Frequency', 'Monetary']
COUPON_COST = 5.0
MARGIN = 0.3


def map_cate_to_score_and_segment(cate, prob_c, max_cate, min_cate_positive, min_cate_negative):
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


def predict_pipeline(rfm_df, uplift_models):
    X = rfm_df[FEATURES]
    prob_c = uplift_models['control_model'].predict_proba(X)[:, 1]
    prob_t = uplift_models['treatment_model'].predict_proba(X)[:, 1]
    cate = prob_t - prob_c
    result = rfm_df.copy()
    result['prob_c'] = prob_c
    result['prob_t'] = prob_t
    result['CATE'] = cate

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


st.set_page_config(page_title="Uplift Marketing AI Dashboard", layout="wide")

_IN_STREAMLIT = False
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    _IN_STREAMLIT = get_script_run_ctx() is not None
except Exception:
    pass

df = None
df_pred = None


@st.cache_data
def load_data():
    return pd.read_csv(RFM_FILE)


@st.cache_resource
def load_models():
    with open(UPLIFT_MODEL_FILE, "rb") as f:
        return pickle.load(f)


@st.cache_data
def get_predictions(rfm):
    return predict_pipeline(rfm, models)


if _IN_STREAMLIT:
    df = load_data()
    models = load_models()
    df_pred = get_predictions(df)

st.title("AI Marketing Uplift Dashboard")
st.markdown("Uplift prediction system using XGBoost T-Learner.")
tab1, tab2, tab3 = st.tabs(["What-If Targeting", "Executive Summary", "Customer Lookup"])

with tab1:
    st.header("Profit Simulation (What-If Slider)")
    col1, col2 = st.columns(2)
    with col1:
        coupon_cost = st.slider("Coupon Cost ($)", 1.0, 50.0, COUPON_COST, 1.0)
    with col2:
        margin = st.slider("Expected Margin (%)", 5, 100, int(MARGIN * 100), 5) / 100.0
    st.markdown("### AI Recommendations")
    df_pred['Expected_Profit_Uplift'] = df_pred['CATE'] * df_pred['Monetary'] * margin - coupon_cost
    df_pred['Action'] = np.where(df_pred['Expected_Profit_Uplift'] > 0, "Target", "Do Not Target")
    num_targets = df_pred[df_pred['Action'] == "Target"].shape[0]
    st.metric("Customers to Target", f"{num_targets} / {len(df_pred)}")
    if num_targets > 0:
        st.dataframe(
            df_pred[df_pred['Action'] == "Target"]
            [['CustomerID', 'Recency', 'Frequency', 'Monetary', 'CATE', 'Expected_Profit_Uplift', 'Action']]
            .sort_values('Expected_Profit_Uplift', ascending=False).head(100)
        )
    else:
        st.warning("No profitable customers at this cost.")

with tab2:
    st.header("Executive Summary")
    mass_cost = len(df_pred) * coupon_cost
    mass_revenue = (df_pred['CATE'] * df_pred['Monetary'] * margin).sum()
    mass_profit = mass_revenue - mass_cost
    mass_roi = (mass_profit / mass_cost) * 100 if mass_cost > 0 else 0
    target_df = df_pred[df_pred['Action'] == "Target"]
    target_cost = len(target_df) * coupon_cost
    target_revenue = (target_df['CATE'] * target_df['Monetary'] * margin).sum()
    target_profit = target_revenue - target_cost
    target_roi = (target_profit / target_cost) * 100 if target_cost > 0 else 0
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Mass Mailing")
        st.metric("Total Cost", f"${mass_cost:,.2f}")
        st.metric("Expected Net Profit", f"${mass_profit:,.2f}")
        st.metric("ROI", f"{mass_roi:.2f}%")
    with col_m2:
        st.subheader("AI Targeted")
        st.metric("Total Cost", f"${target_cost:,.2f}")
        st.metric("Expected Net Profit", f"${target_profit:,.2f}")
        st.metric("ROI", f"{target_roi:.2f}%")
    st.markdown("---")
    st.success(
        f"**Conclusion:** AI targeting saves **${(mass_cost - target_cost):,.2f}** "
        f"(Mass ROI: {mass_roi:.2f}%, Target ROI: {target_roi:.2f}%)."
    )

with tab3:
    st.header("Customer Segment Lookup")
    cid = st.number_input("Enter Customer ID:", min_value=10000, value=12348, step=1)
    cust = df_pred[df_pred['CustomerID'] == cid]
    if not cust.empty:
        c = cust.iloc[0]
        st.write(
            f"**Recency:** {c['Recency']} | **Frequency:** {c['Frequency']} "
            f"| **Monetary:** ${c['Monetary']:,.2f}"
        )
        st.write(f"**CATE:** {c['CATE']:.4f}")
        st.write(f"**Expected Net Profit:** ${c['Expected_Profit_Uplift']:.2f}")
        if c['Action'] == "Target":
            st.success("AI Recommendation: TARGET")
        else:
            st.error("AI Recommendation: DO NOT TARGET")
    else:
        st.warning("Customer ID not found.")
