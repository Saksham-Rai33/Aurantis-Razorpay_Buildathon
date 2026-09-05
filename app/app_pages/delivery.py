import streamlit as st

from app.integrations import (
    CUSTOMER_PHONE,
    check_otp_verification,
    create_envelope_docusign,
    is_docusign_configured,
    is_verify_configured,
    start_otp_verification,
)
from app.services import (
    TIER_BADGE_CLASS,
    TIER_SCORE_CLASS,
    get_risk_tier,
    is_ready_for_delivery,
    mark_delivered,
    mark_otp_sent,
    mark_otp_verified,
    required_actions,
    sign_esign,
    simulate_send_esign,
    simulate_send_otp,
    verify_otp,
)

st.subheader("Delivery")
st.caption("Trigger OTP / e-signature verification and confirm delivery")

ESIGN_OVERRIDE_EMAIL = "sakybrd@gmail.com"

orders = st.session_state.orders
pending = sorted((o for o in orders if not o["delivered"]), key=lambda o: o["risk_score"], reverse=True)

if not pending:
    st.success("All orders delivered.", icon=":material/task_alt:")
    st.stop()

selected_id = st.session_state.get("selected_delivery_order_id")
selected = next((o for o in pending if o["order_id"] == selected_id), None)


def trigger_delivery_simulation(order, tier):
    actions = required_actions(tier)
    needs_esign = "esign" in actions

    if is_verify_configured():
        otp_result = start_otp_verification()
        if otp_result["success"]:
            mark_otp_sent(order, code=None, provider="verify")
        else:
            simulate_send_otp(order)
    else:
        simulate_send_otp(order)
        otp_result = {
            "success": False,
            "simulated": True,
            "detail": "Twilio Verify not configured — simulated OTP.",
        }
    st.session_state[f"sms_result_{order['order_id']}"] = otp_result

    if needs_esign:
        docusign_result = {"success": False, "simulated": True, "detail": ""}
        if is_docusign_configured():
            docusign_result = create_envelope_docusign(
                order["customer_name"], ESIGN_OVERRIDE_EMAIL, order["order_id"],
            )
        if not docusign_result["success"]:
            link = simulate_send_esign(order)
            st.session_state[f"esign_link_{order['order_id']}"] = link
        st.session_state[f"docusign_result_{order['order_id']}"] = docusign_result


tab_queue, tab_customer = st.tabs(["📋 Ready to deliver", "📱 Customer delivery screen"])

with tab_queue:
    st.markdown("<h3>Ready to deliver</h3>", unsafe_allow_html=True)

    card_cols = st.columns(3, gap="medium")
    for i, order in enumerate(pending):
        tier = get_risk_tier(order["risk_score"])
        badge_class = TIER_BADGE_CLASS[tier]
        score_class = TIER_SCORE_CLASS[tier]
        phone = order.get("phone") or CUSTOMER_PHONE

        with card_cols[i % 3]:
            with st.container(border=True, key=f"order_card_{order['order_id']}"):
                st.markdown(
                    f'<div class="order-id">#{order["order_id"]}</div>'
                    f'<div class="order-meta">{order["customer_name"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="margin:10px 0;">'
                    f'<span class="badge {badge_class}">'
                    f'<span class="risk-score-text {score_class}">{order["risk_score"]:.3f}</span></span>'
                    f'&nbsp;<span class="badge {badge_class}">{tier.upper()}</span></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="order-meta">₹{order["amount"]:,.2f}</div>'
                    f'<div class="order-meta">📞 {phone}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("<br>", unsafe_allow_html=True)

                if order["otp_sent_at"]:
                    if st.button(
                        "View customer screen", key=f"select_deliver_{order['order_id']}",
                        icon=":material/smartphone:", use_container_width=True,
                    ):
                        st.session_state.selected_delivery_order_id = order["order_id"]
                        st.rerun()
                elif st.button(
                    "Simulate delivery", key=f"select_deliver_{order['order_id']}",
                    type="primary", icon=":material/local_shipping:", use_container_width=True,
                ):
                    trigger_delivery_simulation(order, tier)
                    st.session_state.selected_delivery_order_id = order["order_id"]
                    st.rerun()

with tab_customer:
    if not selected:
        st.markdown(
            """
            <div class="placeholder-panel">
                <div class="placeholder-icon">📱</div>
                <div>Pick an order in <b>Ready to deliver</b> and click <b>Simulate delivery</b><br>
                to preview what the customer sees on their phone.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        tier = get_risk_tier(selected["risk_score"])
        actions = required_actions(tier)
        needs_esign = "esign" in actions
        phone = selected.get("phone") or CUSTOMER_PHONE

        top_row = st.columns([5, 1])
        top_row[0].caption(f"Previewing order #{selected['order_id']} — {selected['customer_name']}")
        if top_row[1].button("Change", key="change_delivery_order", icon=":material/close:"):
            del st.session_state["selected_delivery_order_id"]
            st.rerun()

        sms_result = st.session_state.get(f"sms_result_{selected['order_id']}", {})
        docusign_result = st.session_state.get(f"docusign_result_{selected['order_id']}", {})
        esign_link = st.session_state.get(f"esign_link_{selected['order_id']}")

        with st.container(border=True, key="phone_screen_card"):
            st.markdown(
                """
                <div class="phone-notch"></div>
                <div class="phone-statusbar"><span>9:41</span><span>Aurantis</span><span>🔋 100%</span></div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="phone-app-header">
                    <div class="avatar">A</div>
                    <div>
                        <div class="contact-name">Aurantis Delivery</div>
                        <div class="contact-sub">to {phone}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if selected.get("otp_provider") == "verify":
                otp_msg = (
                    "🔐 Your Aurantis delivery OTP has been sent to your phone. Enter the code "
                    f"you received to confirm delivery of order #{selected['order_id']}."
                )
            else:
                otp_msg = (
                    f"🔐 Your Aurantis delivery OTP for order #{selected['order_id']} is: "
                    f"<b>{selected['otp_code']}</b>"
                )
            st.markdown(
                f'<div class="msg-bubble">{otp_msg}<span class="msg-time">now</span></div>',
                unsafe_allow_html=True,
            )

            if needs_esign:
                if docusign_result.get("success"):
                    esign_msg = (
                        "✍️ Please sign your delivery confirmation — check "
                        f"<b>{ESIGN_OVERRIDE_EMAIL}</b> for the DocuSign link."
                    )
                else:
                    esign_msg = (
                        "✍️ Please sign your delivery confirmation: "
                        f'<a href="{esign_link}">{esign_link}</a>'
                    )
                st.markdown(
                    f'<div class="msg-bubble">{esign_msg}<span class="msg-time">now</span></div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                '<div class="phone-section-label">Confirm receipt</div>',
                unsafe_allow_html=True,
            )

            if selected["otp_verified"]:
                st.success(f"OTP verified at {selected['otp_verified_at']}", icon=":material/check_circle:")
            else:
                with st.container(key="phone_otp_input_wrap"):
                    entered = st.text_input(
                        "Enter OTP code", key=f"otp_input_{selected['order_id']}",
                        label_visibility="collapsed", placeholder="Enter OTP",
                    )
                if st.button(
                    "Verify OTP", key=f"verify_{selected['order_id']}",
                    type="primary", use_container_width=True,
                ):
                    if selected.get("otp_provider") == "verify":
                        check = check_otp_verification(entered)
                        if check["success"]:
                            mark_otp_verified(selected)
                            st.rerun()
                        else:
                            st.error(f"Incorrect OTP. {check.get('detail', '')}", icon=":material/error:")
                    elif verify_otp(selected, entered):
                        st.rerun()
                    else:
                        st.error("Incorrect OTP. Try again.", icon=":material/error:")

            if needs_esign and not selected["esign_signed"]:
                confirmed = st.checkbox(
                    "I have signed the DocuSign delivery confirmation",
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
                with st.container(key="confirm_order_wrap"):
                    if st.button(
                        "Confirm delivery", type="primary", icon=":material/task_alt:",
                        use_container_width=True,
                    ):
                        mark_delivered(selected)
                        del st.session_state["selected_delivery_order_id"]
                        st.toast(f"Order #{selected['order_id']} delivered.", icon=":material/task_alt:")
                        st.rerun()
            else:
                st.caption("Complete OTP verification (and e-signature, if required) before confirming.")
