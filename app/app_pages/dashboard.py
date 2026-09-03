import streamlit as st

from app.services import get_risk_tier

orders = st.session_state.orders

st.subheader("Dashboard")
st.caption("Live overview of today's order risk activity")

total_orders = len(orders)
high_risk = sum(1 for o in orders if get_risk_tier(o["risk_score"]) == "high")
delivered = sum(1 for o in orders if o["delivered"])
money_saved = sum(o["amount"] for o in orders if get_risk_tier(o["risk_score"]) == "high")
flag_rate = high_risk / total_orders if total_orders else 0

st.markdown(
    f"""
    <div class="metric-card-row">
        <div class="metric-card">
            <div class="metric-label">Total orders today</div>
            <div class="metric-value">{total_orders}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">High risk orders</div>
            <div class="metric-value">{high_risk}</div>
            <div class="metric-delta negative">{flag_rate:.1%} flagged</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Orders delivered</div>
            <div class="metric-value">{delivered}</div>
            <div class="metric-delta neutral">of {total_orders} total</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Money saved</div>
            <div class="metric-value">₹{money_saved:,.0f}</div>
            <div class="metric-delta positive">Fraud loss prevented</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

TIER_BADGE_CLASS = {"low": "badge-green", "medium": "badge-yellow", "high": "badge-red"}
TIER_SCORE_CLASS = {"low": "risk-green", "medium": "risk-yellow", "high": "risk-red"}

with st.container(border=True, key="recent_orders_card"):
    st.markdown("<h3>Recent orders</h3>", unsafe_allow_html=True)

    header_cols = st.columns([1.2, 1, 1, 1, 1, 0.8])
    headers = ["Order ID", "Amount", "Risk score", "Risk level", "Status", "Action"]
    for col, label in zip(header_cols, headers):
        col.markdown(f'<div class="table-header">{label}</div>', unsafe_allow_html=True)

    recent = sorted(orders, key=lambda o: o["risk_score"], reverse=True)[:15]

    for order in recent:
        tier = get_risk_tier(order["risk_score"])
        badge_class = TIER_BADGE_CLASS[tier]
        score_class = TIER_SCORE_CLASS[tier]
        status_class = "badge-blue" if order["delivered"] else "badge-grey"
        status_label = "Delivered" if order["delivered"] else "Pending"

        row = st.columns([1.2, 1, 1, 1, 1, 0.8], vertical_alignment="center")
        row[0].markdown(
            f'<div class="order-id">#{order["order_id"]}</div>'
            f'<div class="order-meta">{order["customer_name"]}</div>',
            unsafe_allow_html=True,
        )
        row[1].markdown(f'<div class="order-meta">₹{order["amount"]:,.2f}</div>', unsafe_allow_html=True)
        row[2].markdown(
            f'<span class="badge {badge_class}"><span class="risk-score-text {score_class}">{order["risk_score"]:.3f}</span></span>',
            unsafe_allow_html=True,
        )
        row[3].markdown(f'<span class="badge {badge_class}">{tier.upper()}</span>', unsafe_allow_html=True)
        row[4].markdown(f'<span class="badge {status_class}">{status_label}</span>', unsafe_allow_html=True)
        if row[5].button("View", key=f"view_{order['order_id']}"):
            st.toast(
                f"Order #{order['order_id']} — {order['customer_name']} — "
                f"{order['product_name']} — ₹{order['amount']:,.2f} — risk {order['risk_score']:.3f}",
                icon=":material/receipt_long:",
            )
