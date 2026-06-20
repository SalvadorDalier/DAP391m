import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from flask import Flask, jsonify, request
import pandas as pd
import pickle
import numpy as np
from src import config
from src.models.predict import predict_pipeline

app = Flask(__name__)
df = pd.DataFrame()


def initialize_app():
    global df
    try:
        rfm_df = pd.read_csv(config.RFM_FILE)
        with open(config.UPLIFT_MODEL_FILE, "rb") as f:
            models = pickle.load(f)
        result = predict_pipeline(rfm_df, models)
        result.set_index('CustomerID', inplace=True)
        df = result
        print(f"Initialized API with {len(df)} customers")
    except Exception as e:
        print(f"Error initializing app: {e}")





@app.route('/api/customer/<int:customer_id>', methods=['GET'])
def get_customer_uplift(customer_id):
    if df.empty:
        return jsonify({"error": "Prediction data not available"}), 500
    try:
        cid = float(customer_id)
        if cid in df.index:
            row = df.loc[cid]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            response = {
                "CustomerID": customer_id,
                "Uplift_Score": float(row['Uplift_Score']),
                "Segment_Label": str(row['Segment_Label']),
                "Monetary": float(row['Monetary']),
                "Recency": float(row['Recency']),
                "Frequency": float(row['Frequency']),
                "ML_Stats": {
                    "CATE": float(row['CATE']),
                    "prob_c": float(row['prob_c']),
                    "prob_t": float(row['prob_t'])
                }
            }
            return jsonify(response), 200
        else:
            return jsonify({"error": f"Customer ID {customer_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/top_targets', methods=['GET'])
def get_top_targets():
    if df.empty:
        return jsonify({"error": "Prediction data not available"}), 500
    try:
        sorted_df = df.sort_values(by='Uplift_Score', ascending=False)
        top_20_count = int(len(sorted_df) * 0.2)
        top_targets = sorted_df.head(top_20_count).reset_index()
        top_targets['CustomerID'] = top_targets['CustomerID'].astype(int)
        result = top_targets[['CustomerID', 'Uplift_Score', 'Segment_Label']].to_dict(orient='records')
        return jsonify({"count": top_20_count, "targets": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    initialize_app()
    app.run(debug=config.API_DEBUG, port=config.API_PORT)
