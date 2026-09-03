import streamlit as st

st.subheader("Evidence vault")
st.caption("Proof of delivery for every completed order")

st.markdown(
    """
    <div class="section-card">
        <h3>Coming next</h3>
        <p style="color:#5F6368; font-size:0.92rem;">
            This page will list every delivered order with its risk score, OTP confirmation,
            signature status, and timestamp — with a "Download proof" action per row.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
