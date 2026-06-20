import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.preprocessing import ingest, features, split
from src.models import train, evaluate, predict


def run():
    print("=" * 50)
    print("Online Retail II Analysis")
    print("=" * 50)

    print("\n[1/5] Loading & validating data...")
    df = ingest.load_cleaned_data()
    ingest.validate_data(df)
    print(f"  {len(df):,} rows, {df['Customer ID'].nunique():,} customers")

    print("\n[2/5] Computing RFM features...")
    rfm_df = features.build_rfm_pipeline(df)
    rfm_df.to_csv(config.RFM_FILE, index=False)
    print(f"  RFM saved: {len(rfm_df)} customers")

    print("\n[3/5] Splitting train/test...")
    train_df, test_df = split.build_split_pipeline(rfm_df)
    train_df.to_csv(config.TRAIN_DATA_FILE, index=False)
    test_df.to_csv(config.TEST_DATA_FILE, index=False)
    print(f"  Train: {len(train_df)}, Test: {len(test_df)}")

    print("\n[4/5] Training models...")
    train_result = train.train_pipeline(train_df)
    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    import pickle
    with open(config.BASELINE_MODEL_FILE, 'wb') as f:
        pickle.dump(train_result['baseline'], f)
    with open(config.UPLIFT_MODEL_FILE, 'wb') as f:
        pickle.dump(train_result['uplift_models'], f)
    print(f"  Baseline accuracy: {train_result['baseline_accuracy']:.4f}")
    print(f"  Models saved to {config.MODEL_DIR}")

    print("\n[5/5] Evaluating & predicting...")
    ev = evaluate.evaluate_pipeline(test_df, train_result['uplift_models'])
    print(f"  AUUC:        {ev['auuc']:.4f}")
    print(f"  Random AUUC: {ev['random_auuc']:.4f}")
    print(f"  Qini Gain:   {ev['qini_gain']:.4f}")

    pred_df = predict.predict_pipeline(rfm_df, train_result['uplift_models'])
    pred_df.to_csv(config.PREDICTIONS_FILE, index=False)
    seg_counts = pred_df['Segment_Label'].value_counts()
    print("\n  Segment distribution:")
    for seg, cnt in seg_counts.items():
        print(f"    {seg}: {cnt} ({cnt/len(pred_df)*100:.1f}%)")

    cb = evaluate.cost_benefit_analysis(ev['uplift_preds'], test_df['Monetary'].values)
    target_profit = cb['net_profit'].sum()
    print(f"\n  Total net profit (all deciles): ${target_profit:,.2f}")

    print("\n" + "=" * 50)
    print("Pipeline complete.")
    print("=" * 50)


if __name__ == '__main__':
    run()
