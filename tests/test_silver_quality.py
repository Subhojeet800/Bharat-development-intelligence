
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SILVER_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "world_bank"
    / "india_gdp.csv"
)


# --------------------------------------------------
# EXPECTED SILVER SCHEMA
# --------------------------------------------------

EXPECTED_COLUMNS = {
    "country_code",
    "country_name",
    "indicator_code",
    "indicator_name",
    "year",
    "gdp_usd",
    "unit",
    "ingested_at",
}


# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def load_silver_data() -> pd.DataFrame:
    """Load the Silver GDP dataset for testing."""

    assert SILVER_FILE.is_file(), (
        f"Silver file not found: {SILVER_FILE}. "
        "Run the Silver transformation first."
    )

    return pd.read_csv(SILVER_FILE)


# --------------------------------------------------
# TEST 1: SILVER FILE EXISTS
# --------------------------------------------------

def test_silver_file_exists():
    """Verify that the Silver output file exists."""

    assert SILVER_FILE.is_file()


# --------------------------------------------------
# TEST 2: DATASET IS NOT EMPTY
# --------------------------------------------------

def test_silver_data_is_not_empty():
    """Verify that the Silver dataset contains records."""

    df = load_silver_data()

    assert not df.empty


# --------------------------------------------------
# TEST 3: EXPECTED COLUMNS EXIST
# --------------------------------------------------


def test_silver_has_expected_columns():
    df = load_silver_data()

    actual_columns = set(df.columns)
    missing_columns = EXPECTED_COLUMNS - actual_columns

    assert not missing_columns, (
        f"Missing columns: {missing_columns}. "
        f"Actual columns: {list(df.columns)}"
    )



# --------------------------------------------------
# TEST 4: INDIA GDP DATA
# --------------------------------------------------

def test_silver_contains_india_gdp():
    """Verify country and indicator identifiers."""

    df = load_silver_data()

    assert (df["country_code"] == "IND").all()
    assert (df["indicator_code"] == "NY.GDP.MKTP.CD").all()


# --------------------------------------------------
# TEST 5: VALID AND UNIQUE YEARS
# --------------------------------------------------

def test_silver_years_are_valid_and_unique():
    """Verify that years are valid and contain no duplicates."""

    df = load_silver_data()

    years = pd.to_numeric(
        df["year"],
        errors="coerce",
    )

    assert years.notna().all(), "Invalid or missing years found."

    assert years.between(1960, 2100).all(), (
        "Years outside the expected range were found."
    )

    assert years.is_unique, "Duplicate years were found."


# --------------------------------------------------
# TEST 6: GDP VALUES ARE NUMERIC
# --------------------------------------------------

def test_silver_gdp_values_are_numeric():
    """Verify GDP values are numeric, present and non-negative."""

    df = load_silver_data()

    gdp = pd.to_numeric(
        df["gdp_usd"],
        errors="coerce",
    )

    assert gdp.notna().all(), (
        "Invalid or missing GDP values were found."
    )

    assert (gdp >= 0).all(), (
        "Negative GDP values were found."
    )