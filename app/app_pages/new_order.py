import re
from datetime import datetime, timezone

import streamlit as st

from app.scoring import CARD_TYPES, PRODUCT_CATEGORIES, PRODUCT_CATEGORY_LABELS, score_new_order
from app.services import (
    TIER_BADGE_CLASS,
    TIER_SCORE_CLASS,
    recommended_action_text,
)
from app.state import load_model
from src.features.engineer import FEATURE_COLS

st.subheader("New order")
st.caption("Score a new transaction and confirm it for fulfillment")


def name_from_email(email):
    local = email.split("@")[0]
    cleaned = re.sub(r"[._+]+", " ", local).strip()
    return cleaned.title() if cleaned else "New customer"


TIER_CIRCLE_COLOR = {"low": "#00d46a", "medium": "#ffa500", "high": "#ff4d4d"}
TIER_ICON = {"low": ":material/check_circle:", "medium": ":material/gpp_maybe:", "high": ":material/gpp_bad:"}

left, right = st.columns([1, 1], gap="large")

with left:
    with st.container(border=True, key="new_order_form_card"):
        st.markdown("<h3>Transaction details</h3>", unsafe_allow_html=True)

        with st.form("new_order_form"):
            amount = st.number_input("Transaction amount (₹)", min_value=0.0, step=50.0, format="%.2f")
            category = st.selectbox(
                "Product category", PRODUCT_CATEGORIES, format_func=lambda c: PRODUCT_CATEGORY_LABELS[c]
            )
            email = st.text_input("Customer email")
            card_type = st.selectbox("Card type", CARD_TYPES)

            r1c1, r1c2 = st.columns(2)
            billing_city = r1c1.text_input("Billing city")
            shipping_city = r1c2.text_input("Shipping city")

            order_hour = st.slider("Hour of order", min_value=0, max_value=23, value=datetime.now().hour)

            submitted = st.form_submit_button(
                "Analyze risk", type="primary", icon=":material/psychology:", use_container_width=True
            )

        if submitted:
            if amount <= 0:
                st.error("Enter an order amount greater than zero.", icon=":material/error:")
            elif "@" not in email:
                st.error("Enter a valid customer email.", icon=":material/error:")
            else:
                model = load_model()
                pool = st.session_state.orders
                result = score_new_order(
                    model, pool,
                    amount=amount, category=category, email=email,
                    billing_city=billing_city, shipping_city=shipping_city,
                    card_type=card_type, order_hour=order_hour,
                )
                st.session_state.new_order_analysis = {
                    **result,
                    "amount": amount,
                    "category": category,
                    "email": email,
                    "billing_city": billing_city,
                    "shipping_city": shipping_city,
                    "card_type": card_type,
                }

with right:
    analysis = st.session_state.get("new_order_analysis")

    with st.container(border=True, key="risk_assessment_card"):
        if not analysis:
            st.markdown(
                """
                <div class="placeholder-panel">
                    <div class="placeholder-icon">🛡️</div>
                    <div>Fill in the transaction details and click <b>Analyze risk</b><br>
                    to see the risk score, tier, and recommended action.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            tier = analysis["tier"]
            badge_class = TIER_BADGE_CLASS[tier]
            circle_color = TIER_CIRCLE_COLOR[tier]
            percent = max(2, min(100, round(analysis["final_score"] * 100)))

            st.markdown("<h3>Risk assessment</h3>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="risk-circle-wrap">
                    <div class="risk-circle" style="background: conic-gradient({circle_color} {percent}%, #2a2d3e {percent}% 100%);">
                        <div class="risk-circle-inner">
                            <div class="risk-circle-value">{analysis['final_score']:.2f}</div>
                            <div class="risk-circle-label">Risk score</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div style="text-align:center; margin-bottom:8px;">'
                f'<span class="badge {badge_class}">{tier.upper()}</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p style="text-align:center;" class="stCaption">'
                f"Base ML score {analysis['model_score']:.3f} → adjusted to "
                f"{analysis['final_score']:.3f} after {len(analysis['rule_flags'])} "
                f"checkout-risk flag(s)</p>",
                unsafe_allow_html=True,
            )

            action_text = recommended_action_text(tier)
            st.markdown(
                f'<div class="action-box tier-{tier}">'
                f'<span>{action_text}</span></div>',
                unsafe_allow_html=True,
            )

            st.markdown("**Top reasons**")
            reasons_html = "".join(
                f'<li><span class="reason-icon">⚠</span><span>{reason}</span></li>'
                for reason in analysis["top_reasons"]
            )
            st.markdown(f'<ul class="reason-list">{reasons_html}</ul>', unsafe_allow_html=True)

            with st.container(key="confirm_order_wrap"):
                if st.button(
                    "Confirm & add order", type="primary", icon=":material/add_shopping_cart:",
                    use_container_width=True,
                ):
                    new_id = max(o["order_id"] for o in st.session_state.orders) + 1
                    new_order = {
                        "order_id": new_id,
                        "customer_name": name_from_email(analysis["email"]),
                        "product_name": PRODUCT_CATEGORY_LABELS[analysis["category"]],
                        "amount": analysis["amount"],
                        "risk_score": analysis["final_score"],
                        **{col: analysis["features"][col] for col in FEATURE_COLS},
                        "email": analysis["email"],
                        "billing_city": analysis["billing_city"],
                        "shipping_city": analysis["shipping_city"],
                        "card_type": analysis["card_type"],
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "otp_code": None,
                        "otp_provider": None,
                        "otp_sent_at": None,
                        "otp_verified": False,
                        "otp_verified_at": None,
                        "esign_sent_at": None,
                        "esign_signed": False,
                        "esign_signer": None,
                        "esign_signed_at": None,
                        "delivered": False,
                        "delivered_at": None,
                    }
                    st.session_state.orders.append(new_order)
                    del st.session_state["new_order_analysis"]
                    st.toast(f"Order #{new_id} added to the queue.", icon=":material/task_alt:")
                    st.rerun()
