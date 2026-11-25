from src.config import STATE_ALIASES

import pandas as pd

def normalize_state(series):
    normalized = (
        series.astype(str)
        .str.casefold()
        .str.replace("&", " and ", regex=False)
        .str.replace(r"[^a-z0-9]+", " ", regex=True)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    return normalized.replace(STATE_ALIASES)
