import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import xgboost as xgb

st.set_page_config(page_title="Uplift Marketing AI Dashboard", layout="wide")

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RFM_FILE = os.path.join(BASE_DIR, "01_data", "processed", "customer_rfm.csv")
MODEL_FILE = os.path.join(BASE_DIR, "04_models", "saved", "uplift_xgboost_manual.pkl")

@st.cache_data
def load_data():
    df = pd.read_csv(RFM_FILE)
    return df

@st.cache_resource
def load_model():
    with open(MODEL_FILE, "rb") as f:
        models = pickle.load(f)
    return models

df = load_data()
models = load_model()

# Calculate Predictions
@st.cache_data
def get_predictions(df):
    features = ['Recency', 'Frequency', 'Monetary']
    X = df[features]
    
    xgb_control = models['control_model']
    xgb_treatment = models['treatment_model']
    
    prob_c = xgb_control.predict_proba(X)[:, 1]
    prob_t = xgb_treatment.predict_proba(X)[:, 1]
    cate = prob_t - prob_c
    
    df_pred = df.copy()
    df_pred['prob_c'] = prob_c
    df_pred['prob_t'] = prob_t
    df_pred['CATE'] = cate
    return df_pred

df_pred = get_predictions(df)

st.title("🎯 AI Marketing Uplift Dashboard")
st.markdown("Hệ thống tự động đề xuất danh sách khách hàng mục tiêu dựa trên mô hình Machine Learning T-Learner (XGBoost).")

tab1, tab2, tab3 = st.tabs(["🎛️ Công cụ Target (What-if)", "📊 Executive Summary", "🔍 Tra cứu Khách hàng"])

# Tab 1: What-If Slider & Targeting
with tab1:
    st.header("Công cụ Mô phỏng Lợi nhuận (What-If Slider)")
    col1, col2 = st.columns(2)
    with col1:
        coupon_cost = st.slider("Chi phí 1 Coupon ($)", min_value=1.0, max_value=50.0, value=5.0, step=1.0)
    with col2:
        margin = st.slider("Biên Lợi nhuận kỳ vọng (%)", min_value=5, max_value=100, value=30, step=5) / 100.0

    st.markdown("### Khuyến nghị AI (AI Recommendations)")
    
    # Expected Profit Uplift = CATE * Monetary * Margin - coupon_cost
    df_pred['Expected_Profit_Uplift'] = df_pred['CATE'] * df_pred['Monetary'] * margin - coupon_cost
    
    # Target rule: Target if Expected_Profit_Uplift > 0
    df_pred['Action'] = np.where(df_pred['Expected_Profit_Uplift'] > 0, "Target", "Do Not Target")
    
    num_targets = df_pred[df_pred['Action'] == "Target"].shape[0]
    st.metric("Số lượng khách hàng nên Target", f"{num_targets} / {len(df_pred)}")
    
    if num_targets > 0:
        st.dataframe(
            df_pred[df_pred['Action'] == "Target"][['CustomerID', 'Recency', 'Frequency', 'Monetary', 'CATE', 'Expected_Profit_Uplift', 'Action']]
            .sort_values('Expected_Profit_Uplift', ascending=False)
            .head(100)
        )
    else:
        st.warning("Với mức chi phí này, không có khách hàng nào mang lại lợi nhuận dương nếu phát coupon.")

# Tab 2: Executive Summary
with tab2:
    st.header("Executive Summary: So sánh Hiệu quả Chiến dịch")
    st.markdown("Dựa trên các thiết lập ở tab What-If, dưới đây là tổng ngân sách và ROI so sánh giữa việc gửi đại trà (Mass Mailing) và gửi có chọn lọc bằng AI (Targeted Mailing).")
    
    # 1. Mass Mailing
    mass_cost = len(df_pred) * coupon_cost
    mass_revenue = (df_pred['CATE'] * df_pred['Monetary'] * margin).sum()
    mass_profit = mass_revenue - mass_cost
    mass_roi = (mass_profit / mass_cost) * 100 if mass_cost > 0 else 0
    
    # 2. AI Targeted Mailing
    target_df = df_pred[df_pred['Action'] == "Target"]
    target_cost = len(target_df) * coupon_cost
    target_revenue = (target_df['CATE'] * target_df['Monetary'] * margin).sum()
    target_profit = target_revenue - target_cost
    target_roi = (target_profit / target_cost) * 100 if target_cost > 0 else 0
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.subheader("📬 Mass Mailing (Gửi đại trà)")
        st.metric("Tổng ngân sách (Cost)", f"${mass_cost:,.2f}")
        st.metric("Lợi nhuận ròng dự kiến", f"${mass_profit:,.2f}")
        st.metric("ROI", f"{mass_roi:.2f}%")
        
    with col_m2:
        st.subheader("🎯 AI Targeted (Dùng ML)")
        st.metric("Tổng ngân sách (Cost)", f"${target_cost:,.2f}")
        st.metric("Lợi nhuận ròng dự kiến", f"${target_profit:,.2f}")
        st.metric("ROI", f"{target_roi:.2f}%")
        
    st.markdown("---")
    st.success(f"**Kết luận:** Áp dụng AI giúp công ty tiết kiệm **${(mass_cost - target_cost):,.2f}** ngân sách rác, đồng thời đạt được ROI cao hơn mức gửi đại trà (Mass ROI: {mass_roi:.2f}%, Target ROI: {target_roi:.2f}%).")

# Tab 3: Tra cứu Khách hàng
with tab3:
    st.header("Tra cứu Phân khúc Khách hàng Cá nhân")
    cid = st.number_input("Nhập Customer ID (VD: 12348, 17592):", min_value=10000, value=12348, step=1)
    cust = df_pred[df_pred['CustomerID'] == cid]
    if not cust.empty:
        c = cust.iloc[0]
        st.write(f"**Recency:** {c['Recency']} | **Frequency:** {c['Frequency']} | **Monetary:** ${c['Monetary']:,.2f}")
        st.write(f"**CATE (Xác suất mua hàng tăng thêm):** {c['CATE']:.4f}")
        st.write(f"**Lợi nhuận kỳ vọng ròng:** ${c['Expected_Profit_Uplift']:.2f}")
        
        if c['Action'] == "Target":
            st.success("✅ **AI Khuyến nghị: TARGET (Nên gửi Coupon)**")
        else:
            st.error("❌ **AI Khuyến nghị: DO NOT TARGET (Không gửi, tránh lỗ)**")
    else:
        st.warning("Không tìm thấy Customer ID này trong cơ sở dữ liệu.")
