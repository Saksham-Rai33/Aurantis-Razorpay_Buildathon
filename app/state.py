import copy

import joblib
import streamlit as st

from app.data_gen import generate_demo_orders

MODEL_PATH = "results/model.pkl"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def base_demo_orders():
    return generate_demo_orders()


def ensure_state():
    if "orders" not in st.session_state:
        with st.spinner("Scoring demo orders with trained model..."):
            st.session_state.orders = copy.deepcopy(base_demo_orders())
    load_model()
