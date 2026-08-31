import pandas as pd
import numpy as np
import lightgbm as lgb
import json
import joblib
from src.evaluation.cost_curve import run_cost_analysis
from pathlib import Path
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

from src.data.loader import load_raw
from src.data.labeling import generate_labels
from src.features.engineer import run_pipeline
from src.features.preprocess import split_data, apply_smote

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

RANDOM_SEED = 42


def train_model(X_train, y_train):
    print("Training LightGBM model...")
    model = lgb.LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=31,
        max_depth=6,
        min_child_samples=20,
        scale_pos_weight=10,
        random_state=RANDOM_SEED,
        verbosity=-1
    )
    model.fit(X_train, y_train)
    print("Training complete.")
    joblib.dump(model, "results/model.pkl")
    print("Model saved to results/model.pkl")
    return model


def evaluate_model(model, X_test, y_test):
    print("\nEvaluating on held-out test set...")
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
        "pr_auc": round(average_precision_score(y_test, y_prob), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1": round(f1_score(y_test, y_pred), 4),
    }

    print(f"\n── Results ──────────────────────────")
    print(f"  ROC-AUC:   {metrics['roc_auc']}")
    print(f"  PR-AUC:    {metrics['pr_auc']}  ← primary metric")
    print(f"  Precision: {metrics['precision']}")
    print(f"  Recall:    {metrics['recall']}")
    print(f"  F1:        {metrics['f1']}")
    print(f"\n{classification_report(y_test, y_pred)}")

    with open(RESULTS_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("Metrics saved to results/metrics.json")

    optimal = run_cost_analysis(np.array(y_test), y_prob)
    metrics["optimal_threshold"] = optimal["threshold"]
    return metrics, y_prob


if __name__ == "__main__":
    df = load_raw()
    df = generate_labels(df)
    df = run_pipeline(df)

    X_train, X_test, y_train, y_test = split_data(df)
    X_train_sm, y_train_sm = apply_smote(X_train, y_train)

    model = train_model(X_train_sm, y_train_sm)
    metrics, y_prob = evaluate_model(model, X_test, y_test) 