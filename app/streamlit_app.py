import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import copy

import joblib
import pandas as pd
import streamlit as st

from app.data_gen import generate_demo_orders
from app.services import (
    get_risk_tier,
    required_actions,
    simulate_send_otp,
    simulate_send_esign,
    verify_otp,
    sign_esign,
    is_ready_for_delivery,
    mark_delivered,
)

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


def find_order(orders, order_id):
    for o in orders:
        if o["order_id"] == order_id:
            return o
    return None


def render_delivery_simulation(orders):
    st.subheader("Delivery Simulation")

    pending = [o for o in orders if not o["delivered"]]
    if not pending:
        st.success("All orders delivered.")
        return

    labels = [f"#{o['order_id']} — {o['customer_name']} ({o['product_name']})" for o in pending]
    choice = st.selectbox("Select a pending order", labels)
    order = pending[labels.index(choice)]

    tier = get_risk_tier(order["risk_score"])
    actions = required_actions(tier)

    st.markdown(f"**Risk score:** {order['risk_score']:.3f} — **Tier:** :{'green' if tier == 'low' else 'orange' if tier == 'medium' else 'red'}[{tier.upper()}]")
    st.markdown(f"**Required actions:** {', '.join(actions)}")
    if "manual_review" in actions:
        st.warning("Flagged for manual review.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**MSG91 — OTP**")
        if st.button("Simulate MSG91 → Send OTP", key=f"otp_{order['order_id']}"):
            code = simulate_send_otp(order)
            st.rerun()
        if order["otp_sent_at"]:
            st.info(f"OTP sent at {order['otp_sent_at']}\n\nSimulated SMS to {order['phone']}: your code is **{order['otp_code']}**")

    with col2:
        if "esign" in actions:
            st.markdown("**DocuSign — e-signature**")
            if st.button("Simulate DocuSign → Send e-sign link", key=f"esign_{order['order_id']}"):
                link = simulate_send_esign(order)
                st.session_state[f"esign_link_{order['order_id']}"] = link
                st.rerun()
            if order["esign_sent_at"]:
                link = st.session_state.get(f"esign_link_{order['order_id']}", "")
                st.info(f"E-sign link sent at {order['esign_sent_at']}\n\nSimulated DocuSign envelope: {link}")
        else:
            st.markdown("**DocuSign — e-signature**")
            st.caption("Not required for this tier.")


def render_otp_verification(orders):
    st.subheader("OTP Verification")
    st.caption("Delivery agent view")

    awaiting = [o for o in orders if not o["delivered"] and o["otp_sent_at"]]
    if not awaiting:
        st.info("No orders awaiting verification. Send an OTP from the Delivery Simulation tab first.")
        return

    labels = [f"#{o['order_id']} — {o['customer_name']} ({o['product_name']})" for o in awaiting]
    choice = st.selectbox("Select an order awaiting verification", labels, key="otp_verify_select")
    order = awaiting[labels.index(choice)]

    tier = get_risk_tier(order["risk_score"])
    actions = required_actions(tier)
    needs_esign = "esign" in actions

    st.markdown(f"**Tier:** {tier.upper()} — **Required actions:** {', '.join(actions)}")

    st.markdown("**Step 1 — Verify OTP**")
    if order["otp_verified"]:
        st.success(f"OTP verified at {order['otp_verified_at']}")
    else:
        entered = st.text_input("Enter OTP code", key=f"otp_input_{order['order_id']}")
        if st.button("Verify", key=f"otp_verify_{order['order_id']}"):
            if verify_otp(order, entered):
                st.rerun()
            else:
                st.error("Incorrect OTP. Try again.")

    if needs_esign:
        st.markdown("**Step 2 — Capture e-signature**")
        if order["esign_signed"]:
            st.success(f"Signed by {order['esign_signer']} at {order['esign_signed_at']}")
        elif not order["esign_sent_at"]:
            st.warning("E-sign link not yet sent — go to Delivery Simulation first.")
        else:
            signer_name = st.text_input("Signer name", value=order["customer_name"], key=f"signer_{order['order_id']}")
            if st.button("Sign", key=f"esign_sign_{order['order_id']}"):
                sign_esign(order, signer_name)
                st.rerun()

    st.markdown("**Step 3 — Mark delivered**")
    if is_ready_for_delivery(order):
        if st.button("Mark Delivered", key=f"deliver_{order['order_id']}"):
            mark_delivered(order)
            st.rerun()
    else:
        st.caption("Complete all required actions above before marking delivered.")


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
        render_delivery_simulation(st.session_state.orders)
    with tab3:
        render_otp_verification(st.session_state.orders)
    with tab4:
        st.info("Evidence Vault — coming soon.")


if __name__ == "__main__":
    main()
