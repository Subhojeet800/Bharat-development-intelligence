
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_FILE = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "world_bank"
    / "india_gdp.json"
)

SILVER_DIR = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "world_bank"
)

SILVER_FILE = SILVER_DIR / "india_gdp.csv"


def transform_world_bank_gdp() -> pd.DataFrame:
    """Flatten and validate Bronze GDP observations into Silver."""
    print("Starting World Bank GDP transformation...")
    if not BRONZE_FILE.exists():
        raise FileNotFoundError(
            f"Bronze input not found: {BRONZE_FILE}"
        )

    with BRONZE_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if (
        not isinstance(data, list)
        or len(data) < 2
        or not isinstance(data[1], list)
    ):
        raise ValueError(
            "Unexpected World Bank response structure."
        )

    observations = data[1]

    rows = []

    for item in observations:
        if not isinstance(item, dict):
            continue

        country = item.get("country") or {}
        indicator = item.get("indicator") or {}

        rows.append(
            {
                "country_code": item.get("countryiso3code"),
                "country_name": country.get("value"),
                "indicator_code": indicator.get("id"),
                "indicator_name": indicator.get("value"),
                "year": item.get("date"),
                "gdp_usd": item.get("value"),
                "unit": item.get("unit"),
                "ingested_at": pd.Timestamp.now(tz="UTC").isoformat(),
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        raise ValueError("No observations found in Bronze data.")

    # Standardize types.
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["gdp_usd"] = pd.to_numeric(
        df["gdp_usd"],
        errors="coerce",
    )

    # Reject records that violate the expected identity or year.
    valid = (
        (df["country_code"] == "IND")
        & (df["indicator_code"] == "NY.GDP.MKTP.CD")
        & df["year"].between(1900, pd.Timestamp.now().year + 1)
    )

    invalid_count = int((~valid).sum())

    if invalid_count:
        raise ValueError(
            f"Silver transformation rejected {invalid_count} "
            "records with invalid country, indicator, or year."
        )

    # Duplicate country-indicator-year records must not pass.
    duplicate_mask = df.duplicated(
        subset=["country_code", "indicator_code", "year"],
        keep=False,
    )

    if duplicate_mask.any():
        raise ValueError(
            "Duplicate country-indicator-year records detected."
        )

    # GDP can legitimately be null in some reporting periods.
    # Preserve those rows rather than fabricating values.
    df = df.sort_values("year").reset_index(drop=True)

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SILVER_FILE, index=False)

    print("\nSILVER TRANSFORMATION COMPLETE")
    print("=" * 45)
    print(f"Rows written : {len(df)}")
    print(f"Columns      : {len(df.columns)}")
    print(f"Output       : {SILVER_FILE.relative_to(PROJECT_ROOT)}")
    print(f"Null GDP     : {int(df['gdp_usd'].isna().sum())}")
    print("=" * 45)

    return df


if __name__ == "__main__":
    transform_world_bank_gdp()
