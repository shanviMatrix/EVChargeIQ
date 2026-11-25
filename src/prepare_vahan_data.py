
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "raw" / "table_data.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "vahan_ev_registrations.csv"

# Load original VAHAN report
df = pd.read_csv(INPUT_FILE)

# First column contains fuel categories
fuel_column = df.columns[0]

# Find the Total row
total_rows = df[
    df[fuel_column].astype(str).str.strip().str.casefold() == "total"
]

if len(total_rows) != 1:
    raise ValueError("Expected exactly one Total row in VAHAN data.")

total_row = total_rows.iloc[0]

# Exclude the fuel column and the national Total column
state_columns = [
    column for column in df.columns
    if column not in [fuel_column, "Total"]
]

# Convert the Total row into state-wise records
result = pd.DataFrame({
    "state": state_columns,
    "annual_ev_registrations": [
        pd.to_numeric(total_row[state], errors="raise")
        for state in state_columns
    ]
})

result["financial_year"] = "2024-2025"
result["status"] = "ACTIVE"

# Validation
if result["state"].nunique() != 36:
    raise ValueError("Expected 36 unique states/UTs.")

if result["annual_ev_registrations"].isna().any():
    raise ValueError("Missing registration counts.")

if (result["annual_ev_registrations"] < 0).any():
    raise ValueError("Negative registration counts found.")

# Save processed dataset
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(OUTPUT_FILE, index=False)

print("=" * 50)
print("EVChargeIQ - VAHAN DATA PREPROCESSING")
print("=" * 50)

print("Total states/UTs:", len(result))
print(
    "Total EV registrations:",
    f"{result['annual_ev_registrations'].sum():,}"
)

print("\nTop 10 states by EV registrations:")
print(
    result.nlargest(10, "annual_ev_registrations")[
        ["state", "annual_ev_registrations"]
    ].to_string(index=False)
)

print("\nSaved:", OUTPUT_FILE)
