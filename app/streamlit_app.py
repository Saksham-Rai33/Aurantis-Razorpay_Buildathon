import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app.state import ensure_state
from app.styles import CUSTOM_CSS

ICON_PATH = Path(__file__).resolve().parent / "assets" / "aurantis_icon.svg"

st.set_page_config(page_title="Aurantis", page_icon=str(ICON_PATH), layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.logo(str(ICON_PATH), icon_image=str(ICON_PATH), size="large")

ensure_state()

with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="brand-name">🛡️ Aurantis</div>
            <div class="brand-tagline">AI-Powered Return Risk Protection</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

page = st.navigation(
    {
        "": [
            st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/shield:", default=True),
            st.Page("app_pages/new_order.py", title="New Order", icon=":material/add_shopping_cart:"),
            st.Page("app_pages/delivery.py", title="Delivery", icon=":material/local_shipping:"),
            st.Page("app_pages/evidence_vault.py", title="Evidence Vault", icon=":material/lock:"),
        ]
    },
    position="sidebar",
)

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-status">
            <div class="status-row"><span>Model Status</span><span class="status-value">✅ Active</span></div>
            <div class="status-row"><span>Threshold</span><span class="status-value threshold">0.95</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

page.run()
