from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import pickle
import os
import xgboost as xgb

app = Flask(__name__)

# Paths
BASE_DIR = r"C:\Users\Lenovo\Desktop\DAP391_project"
RFM_FILE = os.path.join(BASE_DIR, "01_data", "processed", "customer_rfm.csv")
MODEL_FILE = os.path.join(BASE_DIR, "04_models", "saved", "uplift_xgboost_manual.pkl")

# Global DataFrame for API lookups
df = pd.DataFrame()

def map_cate_to_score_and_segment(cate, prob_c, max_cate, min_cate_positive, min_cate_negative):
    """
    Map CATE [-1, 1] and prob_c to Uplift Score (0-100) and Segments.
    """
    if cate > 0.01:
        # Persuadables (75-100)
        range_cate = max_cate - 0.01 if max_cate > 0.01 else 0.01
        score = 75 + ((cate - 0.01) / range_cate) * 25
        score = min(100.0, score)
        return score, 'Persuadables (Target)'
    elif cate < -0.01:
        # Sleeping Dogs (25-50)
        range_cate = -0.01 - min_cate_negative if min_cate_negative < -0.01 else 0.01
        val = ((cate - min_cate_negative) / range_cate) * 24
        score = 25 + max(0, min(24, val))
        return score, 'Sleeping Dogs'
    else:
        if prob_c >= 0.5:
            # Sure Things (50-75)
            score = 50 + ((prob_c - 0.5) / 0.5) * 24
            return score, 'Sure Things'
        else:
            # Lost Causes (0-25)
            score = (prob_c / 0.5) * 24
            return score, 'Lost Causes'

def initialize_app():
    global df
    try:
        print("Loading models and data...")
        # 1. Load Data
        rfm_df = pd.read_csv(RFM_FILE)
        
        # 2. Load Model
        with open(MODEL_FILE, "rb") as f:
            models = pickle.load(f)
            
        xgb_control = models['control_model']
        xgb_treatment = models['treatment_model']
        
        # 3. Predict CATE
        features = ['Recency', 'Frequency', 'Monetary']
        X = rfm_df[features]
        
        prob_c = xgb_control.predict_proba(X)[:, 1]
        prob_t = xgb_treatment.predict_proba(X)[:, 1]
        cate = prob_t - prob_c
        
        rfm_df['prob_c'] = prob_c
        rfm_df['prob_t'] = prob_t
        rfm_df['CATE'] = cate
        
        # Find stats for scaling
        max_cate = rfm_df['CATE'].max()
        min_cate_positive = rfm_df[rfm_df['CATE'] > 0.01]['CATE'].min() if not rfm_df[rfm_df['CATE'] > 0.01].empty else 0.01
        min_cate_negative = rfm_df['CATE'].min()
        
        # 4. Apply Mapping
        scores = []
        segments = []
        for _, row in rfm_df.iterrows():
            s, seg = map_cate_to_score_and_segment(
                row['CATE'], row['prob_c'], 
                max_cate, min_cate_positive, min_cate_negative
            )
            scores.append(s)
            segments.append(seg)
            
        rfm_df['Uplift_Score'] = scores
        rfm_df['Segment_Label'] = segments
        
        # Format Uplift_Score
        rfm_df['Uplift_Score'] = rfm_df['Uplift_Score'].round(2)
        
        # Set index
        rfm_df.set_index('CustomerID', inplace=True)
        df = rfm_df
        
        print(f"Initialized API with {len(df)} customers mapped to segments.")
        
    except Exception as e:
        print(f"Error initializing app: {e}")

initialize_app()

@app.route('/api/customer/<int:customer_id>', methods=['GET'])
def get_customer_uplift(customer_id):
    if df.empty:
        return jsonify({"error": "Prediction data not available"}), 500
        
    try:
        # Convert to float because index in CSV is often loaded as float
        customer_id_f = float(customer_id)
        if customer_id_f in df.index:
            customer_data = df.loc[customer_id_f]
            if isinstance(customer_data, pd.DataFrame):
                customer_data = customer_data.iloc[0]
                
            response = {
                "CustomerID": customer_id,
                "Uplift_Score": float(customer_data['Uplift_Score']),
                "Segment_Label": str(customer_data['Segment_Label']),
                "Monetary": float(customer_data['Monetary']),
                "Recency": float(customer_data['Recency']),
                "Frequency": float(customer_data['Frequency']),
                "ML_Stats": {
                    "CATE": float(customer_data['CATE']),
                    "prob_c": float(customer_data['prob_c']),
                    "prob_t": float(customer_data['prob_t'])
                }
            }
            return jsonify(response), 200
        else:
            return jsonify({"error": f"Customer ID {customer_id} not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/top_targets', methods=['GET'])
def get_top_targets():
    """Returns top 20% of customers based on Uplift Score"""
    if df.empty:
        return jsonify({"error": "Prediction data not available"}), 500
        
    try:
        sorted_df = df.sort_values(by='Uplift_Score', ascending=False)
        top_20_count = int(len(sorted_df) * 0.2)
        top_targets = sorted_df.head(top_20_count)
        
        top_targets = top_targets.reset_index()
        
        # Convert float ID to int for display
        top_targets['CustomerID'] = top_targets['CustomerID'].astype(int)
        
        result = top_targets[['CustomerID', 'Uplift_Score', 'Segment_Label']].to_dict(orient='records')
        return jsonify({
            "count": top_20_count,
            "targets": result
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask API for Customer Uplift Predictions with XGBoost...")
    app.run(debug=True, port=5000)
