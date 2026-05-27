import pandas as pd
import numpy as np
import os

def export_predictions():
    print("Loading test data...")
    test_data_path = r"C:\Users\Lenovo\Desktop\DAP391_project\01_data\train_test\test_data.csv"
    
    if not os.path.exists(test_data_path):
        print(f"Error: Could not find {test_data_path}")
        return

    df = pd.read_csv(test_data_path)
    
    # Calculate RFM-based heuristic Uplift Score instead of random values
    # Normalize Frequency and Monetary (capping at 90th percentile to avoid outliers)
    f_90 = df['Frequency'].quantile(0.9) if df['Frequency'].quantile(0.9) > 0 else 1
    m_90 = df['Monetary'].quantile(0.9) if df['Monetary'].quantile(0.9) > 0 else 1
    
    f_score = np.clip(df['Frequency'] / f_90, 0, 1)
    m_score = np.clip(df['Monetary'] / m_90, 0, 1)
    fm_avg = (f_score + m_score) / 2.0
    
    # Base Uplift logic mapping to segments:
    # 1. Moderate Recency (5-10) -> highest uplift potential (Persuadables) -> Score 70-100
    # 2. Low Recency (<=4) -> already engaged (Sure Things) -> Score 40-70
    # 3. High Recency (>10) -> disengaged (Sleeping Dogs / Lost Causes) -> Score 10-40
    conditions_uplift = [
        (df['Recency'] > 4) & (df['Recency'] <= 10),
        (df['Recency'] <= 4),
        (df['Recency'] > 10)
    ]
    choices_uplift = [
        70 + (fm_avg * 30),
        40 + (fm_avg * 30),
        10 + (fm_avg * 30)
    ]
    df['Uplift_Score'] = np.select(conditions_uplift, choices_uplift, default=0)
    df['Uplift_Score'] = df['Uplift_Score'].round(2)
    
    # Determine Segments based on Uplift Score
    # Persuadables, Sure Things, Lost Causes, Sleeping Dogs
    conditions = [
        (df['Uplift_Score'] >= 75),
        (df['Uplift_Score'] >= 50) & (df['Uplift_Score'] < 75),
        (df['Uplift_Score'] >= 25) & (df['Uplift_Score'] < 50),
        (df['Uplift_Score'] < 25)
    ]
    choices = ['Persuadables (Target)', 'Sure Things', 'Sleeping Dogs', 'Lost Causes']
    df['Segment_Label'] = np.select(conditions, choices, default='Unknown')
    
    # Select final columns for Power BI
    final_df = df[['CustomerID', 'Recency', 'Frequency', 'Monetary', 'Is_Redeemer', 'TotalReturns', 'Uplift_Score', 'Segment_Label']]
    
    output_path = r"C:\Users\Lenovo\Desktop\DAP391_project\01_data\processed\predictions.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    final_df.to_csv(output_path, index=False)
    print(f"Predictions exported successfully to: {output_path}")

if __name__ == "__main__":
    export_predictions()
