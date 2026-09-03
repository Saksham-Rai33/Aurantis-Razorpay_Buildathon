import streamlit as st

st.subheader("New order")
st.caption("Score a new transaction and confirm it for fulfillment")

st.markdown(
    """
    <div class="section-card">
        <h3>Coming next</h3>
        <p style="color:#5F6368; font-size:0.92rem;">
            This page will host the transaction intake form (amount, product category, email,
            billing/shipping address, card type, time), an "Analyze risk" action that scores the
            order and surfaces the top 3 SHAP reasons, and a "Confirm order" action that adds it
            to the live orders list.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
