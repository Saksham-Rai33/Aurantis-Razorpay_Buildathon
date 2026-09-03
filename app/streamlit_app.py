import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app.state import ensure_state
from app.styles import CUSTOM_CSS

ICON_PATH = Path(__file__).resolve().parent / "assets" / "aurantis_icon.svg"
ICON_DATA_URI = "data:image/svg+xml;base64," + base64.b64encode(ICON_PATH.read_bytes()).decode()

st.set_page_config(page_title="Aurantis", page_icon=str(ICON_PATH), layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.logo(str(ICON_PATH), icon_image=str(ICON_PATH), size="large")

ensure_state()

st.markdown(
    f"""
    <div class="aurantis-header">
        <img src="{ICON_DATA_URI}" />
        <div>
            <div class="brand-name">Aurantis</div>
            <div class="brand-tagline">Return-risk intelligence for e-commerce checkout</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.navigation(
    {
        "": [
            st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True),
            st.Page("app_pages/new_order.py", title="New order", icon=":material/add_shopping_cart:"),
            st.Page("app_pages/delivery.py", title="Delivery", icon=":material/local_shipping:"),
            st.Page("app_pages/evidence_vault.py", title="Evidence vault", icon=":material/folder_shared:"),
        ]
    },
    position="sidebar",
)

page.run()
