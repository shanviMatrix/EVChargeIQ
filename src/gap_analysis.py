
"""
EVChargeIQ - EV Adoption and Charging Infrastructure Gap Analysis

Input:
    1. charging_infrastructure.csv
    2. vahan_ev_stock.csv

VAHAN CSV required columns:
    state, ev_stock, as_of_date

ev_stock must represent cumulative registered EV stock,
not registrations during an individual financial year.

Both datasets must represent the same reference date.
"""

from pathlib import Path
import argparse
import re

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INFRASTRUCTURE_FILE = (
    PROJECT_ROOT / "data" / "raw" /
    "charging_infrastructure.csv"
)

EV_DATA_FILE = (
    PROJECT_ROOT / "data" / "raw" /
    "vahan_ev_stock.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "reports" /
    "ev_infrastructure_gap_analysis.csv"
)

DEFAULT_AS_OF_DATE = "2026-03-01"


def normalize_state(value):
    """Standardize state names for dataset matching."""
    value = str(value).strip().casefold()
    value = re.sub(r"\s+", " ", value)
    return value


def load_and_validate_data(
    infrastructure_path,
    ev_data_path,
    reference_date
):
    """Load and validate the two datasets."""

    infrastructure = pd.read_csv(infrastructure_path)
    ev_data = pd.read_csv(ev_data_path)

    required_infrastructure = {
        "state",
        "operational",
        "installed_total"
    }

    required_ev = {
        "state",
        "ev_stock",
        "as_of_date"
    }

    missing_infrastructure = (
        required_infrastructure - set(infrastructure.columns)
    )

    missing_ev = required_ev - set(ev_data.columns)

    if missing_infrastructure:
        raise ValueError(
            f"Infrastructure CSV missing columns: "
            f"{sorted(missing_infrastructure)}"
        )

    if missing_ev:
        raise ValueError(
            f"VAHAN CSV missing columns: {sorted(missing_ev)}"
        )

    infrastructure = infrastructure.copy()
    ev_data = ev_data.copy()

    infrastructure["state"] = (
        infrastructure["state"].map(normalize_state)
    )

    ev_data["state"] = (
        ev_data["state"].map(normalize_state)
    )

    for column in ["operational", "installed_total"]:
        infrastructure[column] = pd.to_numeric(
            infrastructure[column],
            errors="coerce"
        )

    ev_data["ev_stock"] = pd.to_numeric(
        ev_data["ev_stock"],
        errors="coerce"
    )

    ev_data["as_of_date"] = pd.to_datetime(
        ev_data["as_of_date"],
        errors="coerce"
    ).dt.date

    expected_date = pd.to_datetime(reference_date).date()

    if ev_data["as_of_date"].isna().any():
        raise ValueError(
            "Invalid or missing VAHAN reference dates."
        )

    if ev_data["as_of_date"].nunique() != 1:
        raise ValueError(
            "VAHAN data contains multiple reference dates. "
            "Use one consistent snapshot."
        )

    actual_date = ev_data["as_of_date"].iloc[0]

    if actual_date != expected_date:
        raise ValueError(
            f"Date mismatch: expected {expected_date}, "
            f"received {actual_date}."
        )

    if infrastructure[
        ["operational", "installed_total"]
    ].isna().any().any():
        raise ValueError(
            "Infrastructure data contains missing numeric values."
        )

    if ev_data["ev_stock"].isna().any():
        raise ValueError(
            "VAHAN EV stock contains missing or invalid values."
        )

    if (
        infrastructure[["operational", "installed_total"]]
        < 0
    ).any().any():
        raise ValueError(
            "Infrastructure counts cannot be negative."
        )

    if (ev_data["ev_stock"] < 0).any():
        raise ValueError("EV stock cannot be negative.")

    if infrastructure["state"].duplicated().any():
        raise ValueError(
            "Duplicate states found in infrastructure dataset."
        )

    if ev_data["state"].duplicated().any():
        raise ValueError(
            "Duplicate states found in VAHAN dataset. "
            "Aggregate records by state before running analysis."
        )

    return infrastructure, ev_data


def calculate_gap(infrastructure, ev_data):
    """
    Calculate relative infrastructure gaps.

    Benchmark:
        Median EVs per operational charger across states.

    This is a comparative planning indicator, not an
    official infrastructure shortage estimate.
    """

    unmatched_infrastructure = sorted(
        set(infrastructure["state"]) - set(ev_data["state"])
    )

    unmatched_ev = sorted(
        set(ev_data["state"]) - set(infrastructure["state"])
    )

    if unmatched_infrastructure or unmatched_ev:
        raise ValueError(
            "State names do not match between datasets.\n"
            f"Missing in VAHAN: {unmatched_infrastructure}\n"
            f"Missing in infrastructure: {unmatched_ev}\n"
            "Standardize state names before proceeding."
        )

    merged = infrastructure.merge(
        ev_data[["state", "ev_stock"]],
        on="state",
        how="inner",
        validate="one_to_one"
    )

    if merged.empty:
        raise ValueError("No matching state records found.")

    if (merged["operational"] <= 0).any():
        invalid = merged.loc[
            merged["operational"] <= 0, "state"
        ].tolist()

        raise ValueError(
            "Cannot calculate EVs per charger for states with "
            f"zero operational chargers: {invalid}"
        )

    merged["evs_per_operational_charger"] = (
        merged["ev_stock"] / merged["operational"]
    )

    benchmark_ratio = (
        merged["evs_per_operational_charger"].median()
    )

    if benchmark_ratio <= 0:
        raise ValueError(
            "The median EV-to-charger benchmark must be positive."
        )

    merged["benchmark_evs_per_charger"] = benchmark_ratio

    merged["benchmark_required_chargers"] = np.ceil(
        merged["ev_stock"] / benchmark_ratio
    ).astype(int)

    merged["relative_additional_chargers"] = (
        merged["benchmark_required_chargers"]
        - merged["operational"]
    ).clip(lower=0)

    merged["relative_gap_percentage"] = np.where(
        merged["benchmark_required_chargers"] > 0,
        (
            merged["relative_additional_chargers"]
            / merged["benchmark_required_chargers"]
        ) * 100,
        0
    )

    merged["benchmark_status"] = np.where(
        merged["relative_additional_chargers"] > 0,
        "Above median EV-to-charger ratio",
        "At or below median benchmark"
    )

    merged = merged.sort_values(
        "evs_per_operational_charger",
        ascending=False
    )

    return merged, benchmark_ratio


def main():
    parser = argparse.ArgumentParser(
        description="EVChargeIQ infrastructure gap analysis"
    )

    parser.add_argument(
        "--infrastructure",
        default=str(INFRASTRUCTURE_FILE)
    )

    parser.add_argument(
        "--ev-data",
        default=str(EV_DATA_FILE)
    )

    parser.add_argument(
        "--as-of-date",
        default=DEFAULT_AS_OF_DATE
    )

    parser.add_argument(
        "--output",
        default=str(OUTPUT_FILE)
    )

    args = parser.parse_args()

    infrastructure_path = Path(args.infrastructure)
    ev_data_path = Path(args.ev_data)
    output_path = Path(args.output)

    if not infrastructure_path.exists():
        raise FileNotFoundError(
            f"Infrastructure dataset not found: "
            f"{infrastructure_path}"
        )

    if not ev_data_path.exists():
        raise FileNotFoundError(
            f"VAHAN dataset not found: {ev_data_path}"
        )

    infrastructure, ev_data = load_and_validate_data(
        infrastructure_path,
        ev_data_path,
        args.as_of_date
    )

    result, benchmark = calculate_gap(
        infrastructure,
        ev_data
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(output_path, index=False)

    print("=" * 60)
    print("EVChargeIQ - INFRASTRUCTURE GAP ANALYSIS")
    print("=" * 60)

    print(f"Reference date: {args.as_of_date}")
    print(f"States / UTs analyzed: {len(result)}")
    print(
        f"Median EVs per operational charger: "
        f"{benchmark:.2f}"
    )

    print("\nHighest relative infrastructure pressure:")
    print(
        result[
            [
                "state",
                "ev_stock",
                "operational",
                "evs_per_operational_charger",
                "relative_additional_chargers"
            ]
        ].head(10).to_string(index=False)
    )

    print(f"\nResults saved to: {output_path}")

    print(
        "\nIMPORTANT: This is a relative benchmark analysis, "
        "not an official demand-gap estimate."
    )


if __name__ == "__main__":
    main()
