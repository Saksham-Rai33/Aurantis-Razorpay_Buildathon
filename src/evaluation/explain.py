import shap
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

PLOTS_DIR = Path("results/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_shap_plot(model, X_test, max_display=10):
    print("Computing SHAP values...")
    
    # Sample 2000 rows for speed
    sample = X_test.sample(min(2000, len(X_test)), random_state=42)
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(sample)

    # For binary classification shap_values is a list
    if isinstance(shap_values, list):
        sv = shap_values[1]
    else:
        sv = shap_values

    # Summary plot
    plt.figure(figsize=(10, 6))
    shap.summary_plot(
        sv, sample,
        max_display=max_display,
        show=False
    )
    plt.title("Feature Importance — What drives return risk?", fontsize=13)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "shap_summary.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("SHAP plot saved to results/plots/shap_summary.png")


def explain_single_order(model, order: dict) -> dict:
    """
    Explain why a single order got its risk score.
    Returns top 3 reasons in plain English.
    """
    from src.features.engineer import FEATURE_COLS

    row = pd.DataFrame([{col: order.get(col, 0.0) for col in FEATURE_COLS}])
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(row)

    if isinstance(shap_values, list):
        sv = shap_values[1][0]
    else:
        sv = shap_values[0]

    # Map features to plain English
    feature_names = {
        "amt_log": "Transaction amount",
        "amt_is_high": "High value order",
        "card1_freq_log": "Card usage frequency",
        "addr1_freq_log": "Address usage frequency",
        "TransactionAmt": "Transaction amount",
        "C1": "Account activity count",
        "C2": "Card activity count",
        "D1": "Days since last transaction",
        "V1": "Identity signal 1",
        "V2": "Identity signal 2",
    }

    # Get top 3 contributing features
    feature_impacts = list(zip(FEATURE_COLS, sv))
    feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
    top_3 = feature_impacts[:3]

    reasons = []
    for feat, impact in top_3:
        direction = "increases" if impact > 0 else "decreases"
        name = feature_names.get(feat, feat)
        reasons.append(f"{name} {direction} risk")

    return {
        "risk_score": float(model.predict_proba(row)[:, 1][0]),
        "top_reasons": reasons
    }


if __name__ == "__main__":
    from src.data.loader import load_raw
    from src.data.labeling import generate_labels
    from src.features.engineer import run_pipeline, FEATURE_COLS
    from src.features.preprocess import split_data, apply_smote

    model = joblib.load("results/model.pkl")

    df = load_raw()
    df = generate_labels(df)
    df = run_pipeline(df)

    _, X_test, _, _ = split_data(df)
    generate_shap_plot(model, X_test)