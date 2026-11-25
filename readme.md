# EVChargeIQ

**Machine Learning-Based EV Charging Infrastructure Demand Forecasting and Gap Analysis**

## Overview

EVChargeIQ is a Python-based data science project that analyzes electric vehicle charging infrastructure across Indian states and union territories.

The project uses historical government-reported EV public charging station installation data to examine infrastructure expansion, compare states, and experiment with machine learning models for forecasting future infrastructure growth.

## Objectives

- Analyze state-wise charging infrastructure.
- Explore historical infrastructure expansion.
- Compare installed and operational charging stations.
- Examine infrastructure availability indicators.
- Train and compare regression models.
- Present findings through an interactive dashboard.

## Dataset

**Primary source:** Ministry of Heavy Industries, Government of India.

**Publication:** Press Information Bureau, 27 March 2026.

The dataset contains state-wise annual EV public charging station installations from FY 2020–21 to FY 2025–26 (up to 1 March 2026), total installations, decommissioned stations where reported, and operational stations.

Source: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2246042

## Technologies

- Python
- Pandas
- NumPy
- Plotly
- Scikit-learn
- Streamlit

## Machine Learning Algorithms

1. Linear Regression
2. Decision Tree Regressor
3. Random Forest Regressor

## Evaluation Metrics

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R-squared (R²)

## Application Modules

1. India Infrastructure Overview
2. State-wise Infrastructure Analysis
3. Infrastructure Availability Analysis
4. Machine Learning Forecasting
5. Project Methodology

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Limitations

The current prototype uses OMC-reported charging infrastructure data rather than a complete national inventory. The dataset does not yet contain compatible state-year EV registration records. Consequently, the current infrastructure availability indicators must not be interpreted as definitive EV charging demand gaps.

The forecasting model is exploratory and uses a limited number of state-year observations. Predictions are estimates rather than official infrastructure requirements.

## Future Scope

- Integrate VAHAN EV registration data.
- Integrate NITI Aayog electric mobility indicators.
- Develop a more robust infrastructure gap index.
- Improve forecasting with additional historical observations.
- Add geographical maps and state-level insights.


