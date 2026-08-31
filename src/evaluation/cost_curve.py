import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path

RESULTS_DIR = Path("results")
PLOTS_DIR = RESULTS_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Cost model
# FP = we flag a legitimate customer = lost sale
# FN = we miss an abuser = absorbed loss
FP_COST = 800   # INR
FN_COST = 600   # INR


def compute_cost(y_true, y_prob, threshold):
    y_pred = (y_prob >= threshold).astype(int)
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    return {
        "threshold": round(threshold, 3),
        "fp": fp,
        "fn": fn,
        "fp_cost": fp * FP_COST,
        "fn_cost": fn * FN_COST,
        "total_cost": (fp * FP_COST) + (fn * FN_COST),
        "flag_rate": round(float(y_pred.mean()), 4),
    }


def build_cost_curve(y_true, y_prob):
    thresholds = np.linspace(0.05, 0.95, 80)
    rows = [compute_cost(y_true, y_prob, t) for t in thresholds]
    return pd.DataFrame(rows)


def find_optimal_threshold(cost_df):
    idx = cost_df["total_cost"].idxmin()
    optimal = cost_df.loc[idx].to_dict()
    print(f"\n── Optimal Threshold ────────────────")
    print(f"  Threshold:    {optimal['threshold']}")
    print(f"  Total cost:   ₹{optimal['total_cost']:,.0f}")
    print(f"  FP (blocked legit customers): {optimal['fp']:,}")
    print(f"  FN (missed abusers):          {optimal['fn']:,}")
    print(f"  Flag rate:    {optimal['flag_rate']:.2%}")
    return optimal


def plot_cost_curve(cost_df, optimal):
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(cost_df["threshold"], cost_df["total_cost"],
            lw=2, color="#1a73e8", label="Total cost")
    ax.plot(cost_df["threshold"], cost_df["fp_cost"],
            lw=1.5, color="#ea4335", linestyle="--",
            label=f"FP cost (₹{FP_COST}/blocked customer)")
    ax.plot(cost_df["threshold"], cost_df["fn_cost"],
            lw=1.5, color="#fbbc04", linestyle="--",
            label=f"FN cost (₹{FN_COST}/missed abuser)")
    ax.axvline(optimal["threshold"], color="green", lw=2,
               label=f"Optimal threshold = {optimal['threshold']}")

    ax.set_xlabel("Threshold", fontsize=12)
    ax.set_ylabel("Total Business Cost (₹)", fontsize=12)
    ax.set_title("Business Cost vs Threshold — Return Risk Scorer", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "cost_curve.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Cost curve saved to results/plots/cost_curve.png")


def run_cost_analysis(y_true, y_prob):
    cost_df = build_cost_curve(y_true, y_prob)
    optimal = find_optimal_threshold(cost_df)
    plot_cost_curve(cost_df, optimal)

    with open(RESULTS_DIR / "optimal_threshold.json", "w") as f:
        json.dump(optimal, f, indent=2)

    return optimal