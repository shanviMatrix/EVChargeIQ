from pathlib import Path
import pandas as pd
from src.data.preprocessing import normalize_state
from src.config import (
    YEAR_COLUMNS,
    REQUIRED_INFRA_COLUMNS,
    REQUIRED_VAHAN_COLUMNS,
)

def load_infrastructure_data(file_path):

    data = pd.read_csv(file_path)

    missing_columns = [
        column
        for column in REQUIRED_INFRA_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Infrastructure CSV is missing columns: "
            + ", ".join(missing_columns)
        )

    data = data.copy()

    data["state"] = data["state"].astype(str).str.strip()

    numeric_columns = [
        *YEAR_COLUMNS,
        "installed_total",
        "operational",
    ]

    if "decommissioned" in data.columns:
        numeric_columns.append("decommissioned")

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    if data[numeric_columns].isna().any().any():
        raise ValueError(
            "Missing or invalid numeric values found in "
            "the infrastructure dataset."
        )

    if data["state"].duplicated().any():
        duplicates = data.loc[
            data["state"].duplicated(keep=False),
            "state",
        ].unique()

        raise ValueError(
            "Duplicate state records found: "
            + ", ".join(duplicates)
        )

    if (data[numeric_columns] < 0).any().any():
        raise ValueError(
            "Negative values found in infrastructure data."
        )

    if (data["operational"] > data["installed_total"]).any():
        raise ValueError(
            "Operational chargers cannot exceed net installed chargers."
        )

    return data


def load_vahan_data(file_path):

    data = pd.read_csv(file_path)

    missing_columns = [
        column
        for column in REQUIRED_VAHAN_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "VAHAN CSV is missing columns: "
            + ", ".join(missing_columns)
        )

    data = data.copy()

    data["state"] = data["state"].astype(str).str.strip()

    data["annual_ev_registrations"] = pd.to_numeric(
        data["annual_ev_registrations"],
        errors="coerce",
    )

    if data["annual_ev_registrations"].isna().any():
        raise ValueError(
            "Invalid EV registration values found in VAHAN data."
        )

    if (data["annual_ev_registrations"] < 0).any():
        raise ValueError(
            "Negative EV registration values found."
        )

    data["state_key"] = normalize_state(data["state"])

    if data["state_key"].duplicated().any():
        duplicates = data.loc[
            data["state_key"].duplicated(keep=False),
            "state",
        ].unique()

        raise ValueError(
            "Duplicate state records found in VAHAN data: "
            + ", ".join(duplicates)
        )

    return data
