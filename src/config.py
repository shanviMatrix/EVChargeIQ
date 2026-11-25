"""Shared EVChargeIQ configuration constants."""

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


FEATURE_COLUMNS = [
    "state",
    "year_index",
    "current_installations",
    "cumulative_installations",
]


TARGET_COLUMN = "next_year_installations"
