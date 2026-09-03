import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import copy

import joblib
import pandas as pd
import streamlit as st

from app.data_gen import generate_demo_orders
from app.services import get_risk_tier, required_actions

MODEL_PATH = "results/model.pkl"

TIER_COLORS = {"low": "#1a7f37", "medium": "#b58105", "high": "#cf222e"}


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def base_demo_orders():
    return generate_demo_orders()


def init_state():
    if "orders" not in st.session_state:
        with st.spinner("Scoring demo orders with trained model..."):
            st.session_state.orders = copy.deepcopy(base_demo_orders())


def orders_dataframe(orders):
    rows = []
    for o in orders:
        tier = get_risk_tier(o["risk_score"])
        status = "delivered" if o["delivered"] else "pending"
        rows.append({
            "Order ID": o["order_id"],
            "Customer": o["customer_name"],
            "Product": o["product_name"],
            "Amount (₹)": round(o["amount"], 2),
            "Risk Score": round(o["risk_score"], 3),
            "Tier": tier.upper(),
            "Actions Required": ", ".join(required_actions(tier)),
            "Status": status,
        })
    return pd.DataFrame(rows)


def render_dashboard(orders):
    st.subheader("Merchant Dashboard")

    df = orders_dataframe(orders)
    total = len(df)
    low = (df["Tier"] == "LOW").sum()
    medium = (df["Tier"] == "MEDIUM").sum()
    high = (df["Tier"] == "HIGH").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders", total)
    c2.metric("Low Risk", low)
    c3.metric("Medium Risk", medium)
    c4.metric("High Risk", high, delta=f"{high/total:.1%} flag rate", delta_color="inverse")

    def tier_style(row):
        color = TIER_COLORS.get(row["Tier"].lower(), "#000000")
        return [f"color: {color}; font-weight: 600" if col == "Tier" else "" for col in row.index]

    st.dataframe(
        df.style.apply(tier_style, axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount (₹)": st.column_config.NumberColumn(format="%.2f"),
            "Risk Score": st.column_config.NumberColumn(format="%.3f"),
        },
    )


def main():
    st.set_page_config(page_title="Return-Risk Scorer — Merchant Demo", layout="wide")
    st.title("Return-Risk Scorer")
    st.caption("Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager")

    init_state()
    load_model()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Merchant Dashboard",
        "Delivery Simulation",
        "OTP Verification",
        "Evidence Vault",
    ])

    with tab1:
        render_dashboard(st.session_state.orders)
    with tab2:
        st.info("Delivery Simulation — coming soon.")
    with tab3:
        st.info("OTP Verification — coming soon.")
    with tab4:
        st.info("Evidence Vault — coming soon.")


if __name__ == "__main__":
    main()
