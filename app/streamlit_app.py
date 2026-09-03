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
    explain_order,
)

MODEL_PATH = "results/model.pkl"
ICON_PATH = str(Path(__file__).resolve().parent / "assets" / "aurantis_icon.svg")

TIER_COLORS = {"low": "#2DA44E", "medium": "#D97706", "high": "#E5484D"}
TIER_BADGE_COLORS = {"low": "green", "medium": "orange", "high": "red"}
TIER_ICONS = {"low": ":material/check_circle:", "medium": ":material/gpp_maybe:", "high": ":material/gpp_bad:"}


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


def tier_badge(tier):
    st.badge(tier.upper(), color=TIER_BADGE_COLORS[tier], icon=TIER_ICONS[tier])


def orders_dataframe(orders):
    rows = []
    for o in orders:
        tier = get_risk_tier(o["risk_score"])
        status = "Delivered" if o["delivered"] else "Pending"
        rows.append({
            "Order ID": o["order_id"],
            "Customer": o["customer_name"],
            "Product": o["product_name"],
            "Amount (₹)": round(o["amount"], 2),
            "Risk score": o["risk_score"],
            "Tier": tier.upper(),
            "Actions required": ", ".join(required_actions(tier)),
            "Status": status,
        })
    return pd.DataFrame(rows)


def render_dashboard(orders):
    st.subheader("Merchant dashboard")

    df = orders_dataframe(orders)
    total = len(df)
    low = (df["Tier"] == "LOW").sum()
    medium = (df["Tier"] == "MEDIUM").sum()
    high = (df["Tier"] == "HIGH").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total orders", total)
    c2.metric("Low risk", low)
    c3.metric("Medium risk", medium)
    c4.metric("High risk", high, delta=f"{high/total:.1%} flag rate", delta_color="inverse")

    def tier_style(row):
        color = TIER_COLORS.get(row["Tier"].lower(), "#000000")
        return [f"color: {color}; font-weight: 600" if col == "Tier" else "" for col in row.index]

    st.dataframe(
        df.style.apply(tier_style, axis=1),
        hide_index=True,
        column_config={
            "Amount (₹)": st.column_config.NumberColumn(format="%.2f"),
            "Risk score": st.column_config.ProgressColumn(format="percent", min_value=0.0, max_value=1.0),
        },
    )


def render_delivery_simulation(orders):
    st.subheader("Delivery simulation")

    pending = [o for o in orders if not o["delivered"]]
    if not pending:
        st.success("All orders delivered.", icon=":material/task_alt:")
        return

    labels = [f"#{o['order_id']} — {o['customer_name']} ({o['product_name']})" for o in pending]
    choice = st.selectbox("Select a pending order", labels)
    order = pending[labels.index(choice)]

    tier = get_risk_tier(order["risk_score"])
    actions = required_actions(tier)

    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown(f"**Risk score:** {order['risk_score']:.3f}")
            tier_badge(tier)
        st.caption(f"Required actions: {', '.join(actions)}")
        if "manual_review" in actions:
            st.warning("Flagged for manual review.", icon=":material/gpp_maybe:")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("**MSG91 — OTP**")
            if st.button("Simulate MSG91 → send OTP", key=f"otp_{order['order_id']}"):
                simulate_send_otp(order)
                st.rerun()
            if order["otp_sent_at"]:
                st.success(
                    f"OTP sent at {order['otp_sent_at']}\n\n"
                    f"Simulated SMS to {order['phone']}: your code is **{order['otp_code']}**",
                    icon=":material/sms:",
                )

    with col2:
        with st.container(border=True):
            st.markdown("**DocuSign — e-signature**")
            if "esign" in actions:
                if st.button("Simulate DocuSign → send e-sign link", key=f"esign_{order['order_id']}"):
                    link = simulate_send_esign(order)
                    st.session_state[f"esign_link_{order['order_id']}"] = link
                    st.rerun()
                if order["esign_sent_at"]:
                    link = st.session_state.get(f"esign_link_{order['order_id']}", "")
                    st.success(
                        f"E-sign link sent at {order['esign_sent_at']}\n\n"
                        f"Simulated DocuSign envelope: {link}",
                        icon=":material/draw:",
                    )
            else:
                st.caption("Not required for this tier.")


def render_otp_verification(orders):
    st.subheader("OTP verification")
    st.caption("Delivery agent view")

    awaiting = [o for o in orders if not o["delivered"] and o["otp_sent_at"]]
    if not awaiting:
        st.info("No orders awaiting verification. Send an OTP from the delivery simulation tab first.")
        return

    labels = [f"#{o['order_id']} — {o['customer_name']} ({o['product_name']})" for o in awaiting]
    choice = st.selectbox("Select an order awaiting verification", labels, key="otp_verify_select")
    order = awaiting[labels.index(choice)]

    tier = get_risk_tier(order["risk_score"])
    actions = required_actions(tier)
    needs_esign = "esign" in actions

    with st.container(horizontal=True, vertical_alignment="center"):
        tier_badge(tier)
        st.caption(f"Required actions: {', '.join(actions)}")

    with st.container(border=True):
        st.markdown("**Step 1 — Verify OTP**")
        if order["otp_verified"]:
            st.success(f"OTP verified at {order['otp_verified_at']}", icon=":material/check_circle:")
        else:
            entered = st.text_input("Enter OTP code", key=f"otp_input_{order['order_id']}")
            if st.button("Verify", key=f"otp_verify_{order['order_id']}"):
                if verify_otp(order, entered):
                    st.rerun()
                else:
                    st.error("Incorrect OTP. Try again.", icon=":material/error:")

    if needs_esign:
        with st.container(border=True):
            st.markdown("**Step 2 — Capture e-signature**")
            if order["esign_signed"]:
                st.success(f"Signed by {order['esign_signer']} at {order['esign_signed_at']}", icon=":material/draw:")
            elif not order["esign_sent_at"]:
                st.warning("E-sign link not yet sent — go to delivery simulation first.", icon=":material/warning:")
            else:
                signer_name = st.text_input("Signer name", value=order["customer_name"], key=f"signer_{order['order_id']}")
                if st.button("Sign", key=f"esign_sign_{order['order_id']}"):
                    sign_esign(order, signer_name)
                    st.rerun()

    st.markdown("**Step 3 — Mark delivered**")
    if is_ready_for_delivery(order):
        if st.button("Mark delivered", key=f"deliver_{order['order_id']}", type="primary", icon=":material/local_shipping:"):
            mark_delivered(order)
            st.rerun()
    else:
        st.caption("Complete all required actions above before marking delivered.")


def render_evidence_vault(orders, model):
    st.subheader("Evidence vault")

    delivered = [o for o in orders if o["delivered"]]
    if not delivered:
        st.caption("No delivered orders yet.")
        return

    rows = []
    for o in delivered:
        tier = get_risk_tier(o["risk_score"])
        explanation = explain_order(model, o)
        rows.append({
            "Order ID": o["order_id"],
            "Customer": o["customer_name"],
            "Tier": tier.upper(),
            "Risk score": o["risk_score"],
            "Top reasons": "; ".join(explanation["top_reasons"]),
            "OTP code": o["otp_code"],
            "OTP verified at": o["otp_verified_at"],
            "Signer": o["esign_signer"] or "—",
            "Signed at": o["esign_signed_at"] or "—",
            "Delivered at": o["delivered_at"],
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        hide_index=True,
        column_config={
            "Risk score": st.column_config.ProgressColumn(format="percent", min_value=0.0, max_value=1.0),
        },
    )


def render_header():
    header = st.container(horizontal=True, vertical_alignment="center", gap="medium")
    with header:
        st.image(ICON_PATH, width=56)
        with st.container():
            st.title("Aurantis")
            st.caption("Return-risk intelligence for e-commerce checkout — Razorpay AI Buildathon 2026, Track 2")


def main():
    st.set_page_config(page_title="Aurantis", page_icon=ICON_PATH, layout="wide")
    st.logo(ICON_PATH, icon_image=ICON_PATH, size="large")

    render_header()

    init_state()
    model = load_model()

    tab1, tab2, tab3, tab4 = st.tabs([
        ":material/dashboard: Merchant dashboard",
        ":material/local_shipping: Delivery simulation",
        ":material/verified_user: OTP verification",
        ":material/folder_shared: Evidence vault",
    ])

    with tab1:
        render_dashboard(st.session_state.orders)
    with tab2:
        render_delivery_simulation(st.session_state.orders)
    with tab3:
        render_otp_verification(st.session_state.orders)
    with tab4:
        render_evidence_vault(st.session_state.orders, model)


if __name__ == "__main__":
    main()
