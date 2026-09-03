import streamlit as st

st.subheader("Delivery")
st.caption("Trigger OTP / e-signature verification and confirm delivery")

st.markdown(
    """
    <div class="section-card">
        <h3>Coming next</h3>
        <p style="color:#5F6368; font-size:0.92rem;">
            This page will list orders ready to deliver with a "Simulate delivery" action per row —
            low risk sends an OTP via MSG91, medium/high risk adds a DocuSign e-signature link —
            plus an OTP entry box and "Confirm delivery" action for the delivery agent.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
