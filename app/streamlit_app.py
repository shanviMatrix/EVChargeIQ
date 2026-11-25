from pathlib import Path
import sys

# Make the project root available for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import re

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.data.preprocessing import normalize_state
from src.data.loaders import load_infrastructure_data, load_vahan_data
from src.models.training import train_models

from app.pages.overview import render as render_overview
from app.pages.state_analysis import render as render_state_analysis
from app.pages.infrastructure import render as render_infrastructure
from app.pages.ml_forecasting import render as render_ml_forecasting
from app.pages.about import render as render_about


from app.components.splash import show_splash
from app.components.header import show_header
from app.components.sidebar import show_sidebar


from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EVChargeIQ | EV Infrastructure Intelligence",
    page_icon="⚡",
    layout="wide",
)





# ============================================================

# Load external stylesheet
css_path = Path(__file__).resolve().parent / "styles" / "main.css"

if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )

show_splash()

# 2. PROJECT PATHS AND CONSTANTS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INFRASTRUCTURE_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "charging_infrastructure.csv"
)

VAHAN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "vahan_ev_registrations.csv"
)

YEAR_COLUMNS = [
    "FY20_21",
    "FY21_22",
    "FY22_23",
    "FY23_24",
    "FY24_25",
    "FY25_26_partial",
]

FULL_YEAR_COLUMNS = YEAR_COLUMNS[:5]

REQUIRED_INFRA_COLUMNS = [
    "state",
    *YEAR_COLUMNS,
    "installed_total",
    "operational",
]

REQUIRED_VAHAN_COLUMNS = [
    "state",
    "annual_ev_registrations",
    "financial_year",
]


# ============================================================
# 3. STATE NAME NORMALIZATION
# ============================================================

STATE_ALIASES = {
    # Andaman and Nicobar Islands
    "andaman and nicobar": "andaman and nicobar islands",
    "andaman nicobar": "andaman and nicobar islands",
    "andaman and nicobar island": "andaman and nicobar islands",
    "andaman and nicobar islands": "andaman and nicobar islands",

    # Dadra and Nagar Haveli and Daman and Diu
    "ut of dnh and dd": "dadra and nagar haveli and daman and diu",
    "dadra nagar haveli and daman diu": "dadra and nagar haveli and daman and diu",
    "dadra and nagar haveli and daman and diu": "dadra and nagar haveli and daman and diu",

    # Other state aliases
    "orissa": "odisha",
    "pondicherry": "puducherry",
    "uttaranchal": "uttarakhand",
    "nct of delhi": "delhi",
}

# Standardize state names in both datasets



# ============================================================
# 5. LOAD AND VALIDATE VAHAN DATA
# ============================================================



# ============================================================
# 6. APPLICATION HEADER
show_header()


# 7. LOAD MAIN DATASETS
# ============================================================

if not INFRASTRUCTURE_FILE.exists():

    st.error(
        "Infrastructure dataset not found."
    )

    st.code(
        "data/raw/charging_infrastructure.csv"
    )

    st.stop()


if not VAHAN_FILE.exists():

    st.error(
        "VAHAN dataset not found. Run the preprocessing script first."
    )

    st.code(
        "python src/prepare_vahan_data.py"
    )

    st.stop()


try:

    df = load_infrastructure_data(
        str(INFRASTRUCTURE_FILE)
    )

    vahan_df = load_vahan_data(
        str(VAHAN_FILE)
    )

except Exception as error:

    st.error(
        f"Dataset loading error: {error}"
    )

    st.stop()


# ============================================================
# 8. PREPARE HISTORICAL INFRASTRUCTURE DATA
# ============================================================

long_df = df.melt(
    id_vars=["state"],
    value_vars=YEAR_COLUMNS,
    var_name="financial_year",
    value_name="gross_installations",
)

long_df["financial_year"] = pd.Categorical(
    long_df["financial_year"],
    categories=YEAR_COLUMNS,
    ordered=True,
)


# ============================================================
# 9. MACHINE LEARNING DATA PREPARATION
# ============================================================

ml_records = []

for _, state_row in df.iterrows():

    cumulative_installations = 0

    for year_index, year_column in enumerate(
        FULL_YEAR_COLUMNS
    ):

        current_installations = int(
            state_row[year_column]
        )

        cumulative_installations += current_installations

        if year_index < len(FULL_YEAR_COLUMNS) - 1:

            next_year_column = FULL_YEAR_COLUMNS[
                year_index + 1
            ]

            ml_records.append(
                {
                    "state": state_row["state"],

                    "year_index": year_index,

                    "current_installations":
                        current_installations,

                    "cumulative_installations":
                        cumulative_installations,

                    "next_year_installations":
                        int(state_row[next_year_column]),
                }
            )


ml_df = pd.DataFrame(ml_records)

FEATURE_COLUMNS = [
    "state",
    "year_index",
    "current_installations",
    "cumulative_installations",
]

TARGET_COLUMN = "next_year_installations"


# ============================================================
# 10. TRAIN AND EVALUATE MACHINE LEARNING MODELS
# ============================================================



try:

    (
        trained_models,
        results_df,
        prediction_frames,
        train_df,
        test_df,
    ) = train_models(ml_df)

except Exception as error:

    st.error(
        f"Machine learning training error: {error}"
    )

    st.stop()


# ============================================================
# 11. NAVIGATION
page = show_sidebar()


# 12. NATIONAL INFRASTRUCTURE METRICS
# ============================================================

total_installed = int(
    df["installed_total"].sum()
)

total_operational = int(
    df["operational"].sum()
)

operational_rate = (
    total_operational / total_installed * 100
    if total_installed > 0
    else 0
)


# ============================================================

# 13. PAGE ROUTING
page_context = globals()

page_renderers = {
    "Overview": render_overview,
    "State Analysis": render_state_analysis,
    "Infrastructure Analysis": render_infrastructure,
    "ML Forecasting": render_ml_forecasting,
    "About Project": render_about,
}

page_renderers[page](page_context)

# ============================================================

