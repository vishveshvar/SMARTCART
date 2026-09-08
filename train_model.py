"""
SmartCart - Machine Learning Model Training & Evaluation Pipeline
Trains a RandomForestClassifier to predict product purchase probability.
Evaluates Accuracy, Precision, Recall, F1 Score, ROC-AUC, Confusion Matrix,
and Feature Importance, saving trained models and metrics.
"""

import os
import json
import datetime
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

from preprocessing import (
    load_and_merge_data,
    build_preprocessing_pipeline,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES
)

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_FILE = os.path.join(MODELS_DIR, "smartcart_random_forest.pkl")
PIPELINE_FILE = os.path.join(MODELS_DIR, "preprocessing_pipeline.pkl")
METRICS_FILE = os.path.join(MODELS_DIR, "model_metrics.json")

def train_and_evaluate(data_dir=None):
    print("=== Training SmartCart Random Forest Classifier ===")
    
    # 1. Load and merge raw data
    X, y, merged = load_and_merge_data(data_dir)
    print(f"Total dataset records: {len(X)}")
    print(f"Target distribution (Purchased): {y.value_counts().to_dict()}")
    
    # 2. Split dataset: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
    
    # 3. Fit preprocessing pipeline
    preprocessor = build_preprocessing_pipeline()
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)
    
    # Extract feature names after One-Hot Encoding for Feature Importance analysis
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]
    encoded_cat_cols = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
    all_feature_names = NUMERICAL_FEATURES + encoded_cat_cols
    
    # 4. Train RandomForestClassifier
    rf = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=8,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train_transformed, y_train)
    
    # 5. Predictions and evaluation
    y_pred = rf.predict(X_test_transformed)
    y_proba = rf.predict_proba(X_test_transformed)[:, 1]
    
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print("\n--- Model Evaluation Results ---")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1 Score:  {f1 * 100:.2f}%")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"Confusion Matrix:\n {cm}")
    
    # 6. Feature Importance
    raw_importances = rf.feature_importances_
    # Aggregate one-hot encoded categories back to base high-level features for executive display
    high_level_importance = {}
    for col in NUMERICAL_FEATURES:
        idx = all_feature_names.index(col)
        high_level_importance[col] = float(raw_importances[idx])
        
    for cat in CATEGORICAL_FEATURES:
        cat_indices = [i for i, name in enumerate(all_feature_names) if name.startswith(cat + "_")]
        high_level_importance[cat] = float(sum(raw_importances[i] for i in cat_indices))
        
    # Sort descending
    sorted_features = sorted(high_level_importance.items(), key=lambda x: x[1], reverse=True)
    feature_importance_list = [{"feature": k, "importance": round(v * 100, 2)} for k, v in sorted_features]
    
    # 7. Save model, pipeline, and metrics
    joblib.dump(rf, MODEL_FILE)
    joblib.dump(preprocessor, PIPELINE_FILE)
    
    metrics_data = {
        "model_name": "Random Forest Classifier",
        "algorithm": "sklearn.ensemble.RandomForestClassifier",
        "version": "1.0.0",
        "trained_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_records": len(X),
        "train_records": len(X_train),
        "test_records": len(X_test),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "confusion_matrix": {
            "tn": cm[0][0],
            "fp": cm[0][1],
            "fn": cm[1][0],
            "tp": cm[1][1]
        },
        "feature_importance": feature_importance_list,
        "hyperparameters": {
            "n_estimators": 150,
            "max_depth": 12,
            "class_weight": "balanced",
            "random_state": 42
        }
    }
    
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics_data, f, indent=4)
        
    print(f"\nModel saved: {MODEL_FILE}")
    print(f"Pipeline saved: {PIPELINE_FILE}")
    print(f"Metrics saved: {METRICS_FILE}")
    print("=== Training Pipeline Completed Successfully ===")
    return metrics_data

if __name__ == "__main__":
    train_and_evaluate()
