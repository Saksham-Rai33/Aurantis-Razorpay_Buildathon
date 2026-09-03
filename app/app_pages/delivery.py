import streamlit as st

from app.integrations import create_envelope_docusign, send_sms_msg91
from app.services import (
    TIER_BADGE_CLASS,
    TIER_SCORE_CLASS,
    get_risk_tier,
    is_ready_for_delivery,
    mark_delivered,
    required_actions,
    sign_esign,
    simulate_send_esign,
    simulate_send_otp,
    verify_otp,
)

st.subheader("Delivery")
st.caption("Trigger OTP / e-signature verification and confirm delivery")

orders = st.session_state.orders
pending = sorted((o for o in orders if not o["delivered"]), key=lambda o: o["risk_score"], reverse=True)

if not pending:
    st.success("All orders delivered.", icon=":material/task_alt:")
    st.stop()

selected_id = st.session_state.get("selected_delivery_order_id")
selected = next((o for o in pending if o["order_id"] == selected_id), None)

if selected:
    tier = get_risk_tier(selected["risk_score"])
    actions = required_actions(tier)
    needs_esign = "esign" in actions

    with st.container(border=True, key="delivery_detail_card"):
        badge_class = TIER_BADGE_CLASS[tier]
        header_row = st.columns([5, 1], vertical_alignment="center")
        header_row[0].markdown(
            f'<h3 style="margin:0;">Delivery workflow — #{selected["order_id"]} '
            f'{selected["customer_name"]}</h3>',
            unsafe_allow_html=True,
        )
        if header_row[1].button("Close", key="close_delivery_detail", icon=":material/close:"):
            del st.session_state["selected_delivery_order_id"]
            st.rerun()

        st.markdown(f'<span class="badge {badge_class}">{tier.upper()}</span>', unsafe_allow_html=True)
        st.caption(f"Required: {', '.join(actions)}")

        if not selected["otp_sent_at"]:
            if st.button("Simulate delivery", type="primary", icon=":material/local_shipping:"):
                code = simulate_send_otp(selected)
                sms_result = send_sms_msg91(
                    selected["phone"], f"Your Aurantis delivery OTP is {code}. Do not share it."
                )
                st.session_state[f"sms_result_{selected['order_id']}"] = sms_result

                if needs_esign:
                    link = simulate_send_esign(selected)
                    st.session_state[f"esign_link_{selected['order_id']}"] = link
                    docusign_result = create_envelope_docusign(
                        selected["customer_name"],
                        selected.get("email", "customer@example.com"),
                        selected["order_id"],
                    )
                    st.session_state[f"docusign_result_{selected['order_id']}"] = docusign_result
                st.rerun()
        else:
            sms_result = st.session_state.get(f"sms_result_{selected['order_id']}", {})
            if sms_result.get("success"):
                st.success(f"Real SMS sent via MSG91 to {selected['phone']}", icon=":material/sms:")
            else:
                st.info(
                    f"Simulated SMS to {selected['phone']}: your code is **{selected['otp_code']}**",
                    icon=":material/sms:",
                )
                st.caption(sms_result.get("detail", ""))

            if needs_esign:
                docusign_result = st.session_state.get(f"docusign_result_{selected['order_id']}", {})
                esign_link = st.session_state.get(f"esign_link_{selected['order_id']}")
                if docusign_result.get("success"):
                    st.success(
                        f"Real DocuSign envelope sent: {docusign_result.get('link')}",
                        icon=":material/draw:",
                    )
                else:
                    st.info(f"Simulated DocuSign envelope: {esign_link}", icon=":material/draw:")
                    st.caption(docusign_result.get("detail", ""))

            st.markdown("**Delivery agent verification**")

            if selected["otp_verified"]:
                st.success(f"OTP verified at {selected['otp_verified_at']}", icon=":material/check_circle:")
            else:
                entered = st.text_input("Enter OTP code", key=f"otp_input_{selected['order_id']}")
                if st.button("Verify OTP", key=f"verify_{selected['order_id']}"):
                    if verify_otp(selected, entered):
                        st.rerun()
                    else:
                        st.error("Incorrect OTP. Try again.", icon=":material/error:")

            if needs_esign and not selected["esign_signed"]:
                confirmed = st.checkbox(
                    "Customer has completed the DocuSign e-signature",
                    key=f"esign_confirm_{selected['order_id']}",
                )
                if confirmed:
                    sign_esign(selected, selected["customer_name"])
                    st.rerun()
            elif needs_esign:
                st.success(
                    f"Signed by {selected['esign_signer']} at {selected['esign_signed_at']}",
                    icon=":material/draw:",
                )

            if is_ready_for_delivery(selected):
                if st.button("Confirm delivery", type="primary", icon=":material/task_alt:"):
                    mark_delivered(selected)
                    del st.session_state["selected_delivery_order_id"]
                    st.toast(f"Order #{selected['order_id']} delivered.", icon=":material/task_alt:")
                    st.rerun()
            else:
                st.caption("Complete OTP verification (and e-signature, if required) before confirming.")

with st.container(border=True, key="delivery_queue_card"):
    st.markdown("<h3>Ready to deliver</h3>", unsafe_allow_html=True)

    header_cols = st.columns([1.2, 1, 1, 1, 1.1])
    for col, label in zip(header_cols, ["Order ID", "Amount", "Risk score", "Risk level", "Action"]):
        col.markdown(f'<div class="table-header">{label}</div>', unsafe_allow_html=True)

    for order in pending:
        tier = get_risk_tier(order["risk_score"])
        badge_class = TIER_BADGE_CLASS[tier]
        score_class = TIER_SCORE_CLASS[tier]

        row = st.columns([1.2, 1, 1, 1, 1.1], vertical_alignment="center")
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
        if row[4].button("Deliver", key=f"select_deliver_{order['order_id']}"):
            st.session_state.selected_delivery_order_id = order["order_id"]
            st.rerun()
