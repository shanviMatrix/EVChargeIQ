import streamlit as st


def show_sidebar():
    st.sidebar.title("⚡ EVChargeIQ")

    st.sidebar.caption(
        "India EV Infrastructure Analysis"
    )

    return st.sidebar.radio(
        "Navigation",
        [
            "Overview",
            "State Analysis",
            "Infrastructure Analysis",
            "ML Forecasting",
            "About Project",
        ],
    )
