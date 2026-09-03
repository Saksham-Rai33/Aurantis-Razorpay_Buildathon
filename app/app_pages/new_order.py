import re
from datetime import datetime, timezone

import streamlit as st

from app.scoring import CARD_TYPES, PRODUCT_CATEGORIES, score_new_order
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


with st.container(border=True, key="new_order_form_card"):
    st.markdown("<h3>Transaction details</h3>", unsafe_allow_html=True)

    with st.form("new_order_form"):
        r1c1, r1c2 = st.columns(2)
        amount = r1c1.number_input("Amount (₹)", min_value=0.0, step=50.0, format="%.2f")
        category = r1c2.selectbox("Product category", PRODUCT_CATEGORIES)

        r2c1, r2c2 = st.columns(2)
        email = r2c1.text_input("Customer email")
        phone = r2c2.text_input("Phone number", placeholder="9XXXXXXXXX")

        r3c1, r3c2 = st.columns(2)
        billing_address = r3c1.text_input("Billing address")
        shipping_address = r3c2.text_input("Shipping address")

        r4c1, r4c2 = st.columns(2)
        card_type = r4c1.selectbox("Card type", CARD_TYPES)
        order_time = r4c2.time_input("Time", value=datetime.now().time())

        submitted = st.form_submit_button(
            "Analyze risk", type="primary", icon=":material/psychology:"
        )

    if submitted:
        if amount <= 0:
            st.error("Enter an order amount greater than zero.", icon=":material/error:")
        elif "@" not in email:
            st.error("Enter a valid customer email.", icon=":material/error:")
        elif not phone.strip():
            st.error("Enter a phone number for delivery OTP.", icon=":material/error:")
        else:
            model = load_model()
            pool = st.session_state.orders
            result = score_new_order(
                model, pool,
                amount=amount, category=category, email=email,
                billing_address=billing_address, shipping_address=shipping_address,
                card_type=card_type, order_hour=order_time.hour,
            )
            st.session_state.new_order_analysis = {
                **result,
                "amount": amount,
                "category": category,
                "email": email,
                "phone": phone.strip(),
                "billing_address": billing_address,
                "shipping_address": shipping_address,
                "card_type": card_type,
            }

analysis = st.session_state.get("new_order_analysis")
if analysis:
    tier = analysis["tier"]
    badge_class = TIER_BADGE_CLASS[tier]
    score_class = TIER_SCORE_CLASS[tier]

    with st.container(border=True, key="risk_assessment_card"):
        st.markdown("<h3>Risk assessment</h3>", unsafe_allow_html=True)

        st.markdown(
            f'<span class="badge {badge_class}">'
            f'<span class="risk-score-text {score_class}">{analysis["final_score"]:.3f}</span>'
            f'</span>&nbsp;&nbsp;<span class="badge {badge_class}">{tier.upper()}</span>',
            unsafe_allow_html=True,
        )
        st.caption(
            f"Base ML score {analysis['model_score']:.3f} → adjusted to "
            f"{analysis['final_score']:.3f} after {len(analysis['rule_flags'])} "
            f"checkout-risk flag(s)"
        )

        st.markdown("**Top reasons**")
        reasons_html = "".join(f"<li>{reason}</li>" for reason in analysis["top_reasons"])
        st.markdown(f"<ul>{reasons_html}</ul>", unsafe_allow_html=True)

        st.markdown("**Recommended action**")
        action_text = recommended_action_text(tier)
        if tier == "low":
            st.success(action_text, icon=":material/check_circle:")
        elif tier == "medium":
            st.warning(action_text, icon=":material/gpp_maybe:")
        else:
            st.error(action_text, icon=":material/gpp_bad:")

        if st.button("Confirm order", type="primary", icon=":material/add_shopping_cart:"):
            new_id = max(o["order_id"] for o in st.session_state.orders) + 1
            new_order = {
                "order_id": new_id,
                "customer_name": name_from_email(analysis["email"]),
                "phone": analysis["phone"],
                "product_name": analysis["category"],
                "address": analysis["billing_address"],
                "amount": analysis["amount"],
                "risk_score": analysis["final_score"],
                **{col: analysis["features"][col] for col in FEATURE_COLS},
                "email": analysis["email"],
                "billing_address": analysis["billing_address"],
                "shipping_address": analysis["shipping_address"],
                "card_type": analysis["card_type"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "otp_code": None,
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
