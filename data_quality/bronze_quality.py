
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# PROJECT PATHS AND CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BRONZE_FILE = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "world_bank"
    / "india_gdp.json"
)

REPORT_DIR = PROJECT_ROOT / "data_quality" / "results"
REPORT_FILE = REPORT_DIR / "bronze_quality_report.csv"

EXPECTED_COUNTRY_ISO2 = "IN"
EXPECTED_COUNTRY_ISO3 = "IND"
EXPECTED_INDICATOR = "NY.GDP.MKTP.CD"


# ============================================================
# HELPER: RECORD A QUALITY CHECK
# ============================================================

def record_check(
    checks: list[dict[str, str]],
    name: str,
    passed: bool,
    details: str,
) -> None:
    """Append a PASS or FAIL result to the check collection."""

    checks.append(
        {
            "check_name": name,
            "status": "PASS" if passed else "FAIL",
            "details": details,
        }
    )


# ============================================================
# MAIN VALIDATION
# ============================================================

def validate_bronze_data() -> dict[str, Any]:
    """Validate the World Bank India GDP Bronze JSON file."""

    checks: list[dict[str, str]] = []
    observations: list[dict[str, Any]] = []

    # --------------------------------------------------------
    # CHECK 1: FILE EXISTS
    # --------------------------------------------------------

    if not BRONZE_FILE.is_file():
        record_check(
            checks,
            "file_exists",
            False,
            f"Bronze file not found: {BRONZE_FILE}",
        )

        return save_report(checks, 0, 0)

    record_check(
        checks,
        "file_exists",
        True,
        f"File found: {BRONZE_FILE.name}",
    )

    # --------------------------------------------------------
    # CHECK 2: JSON IS READABLE
    # --------------------------------------------------------

    try:
        with BRONZE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        record_check(
            checks,
            "valid_json",
            True,
            "JSON parsed successfully.",
        )

    except (json.JSONDecodeError, OSError) as exc:
        record_check(
            checks,
            "valid_json",
            False,
            str(exc),
        )

        return save_report(checks, 0, 0)

    # --------------------------------------------------------
    # CHECK 3: RESPONSE STRUCTURE
    # World Bank API response: [metadata, observations]
    # --------------------------------------------------------

    structure_ok = (
        isinstance(data, list)
        and len(data) >= 2
        and isinstance(data[1], list)
    )

    record_check(
        checks,
        "response_structure",
        structure_ok,
        "Expected [metadata, observations] structure.",
    )

    if not structure_ok:
        return save_report(checks, 0, 0)

    observations = data[1]

    # --------------------------------------------------------
    # CHECK 4: OBSERVATIONS EXIST
    # --------------------------------------------------------

    record_check(
        checks,
        "observations_present",
        len(observations) > 0,
        f"Observation count: {len(observations)}",
    )

    # --------------------------------------------------------
    # CHECKS 5-8: COUNTRY, INDICATOR, YEAR, VALUE
    # --------------------------------------------------------

    valid_identity = 0
    valid_years: list[str] = []
    invalid_years = 0
    invalid_values = 0
    null_values = 0
    invalid_records = 0

    current_year = datetime.now(timezone.utc).year

    for row in observations:

        if not isinstance(row, dict):
            invalid_records += 1
            continue

        country = row.get("country")
        indicator = row.get("indicator")

        if not isinstance(country, dict):
            country = {}

        if not isinstance(indicator, dict):
            indicator = {}

        # World Bank uses country.id="IN" and
        # countryiso3code="IND" for India.
        country_matches = (
            country.get("id") == EXPECTED_COUNTRY_ISO2
            or row.get("countryiso3code")
            == EXPECTED_COUNTRY_ISO3
        )

        indicator_matches = (
            indicator.get("id") == EXPECTED_INDICATOR
        )

        if country_matches and indicator_matches:
            valid_identity += 1

        # Validate year format and reasonable range.
        year = row.get("date")

        if (
            isinstance(year, str)
            and len(year) == 4
            and year.isdigit()
            and 1900 <= int(year) <= current_year + 1
        ):
            valid_years.append(year)
        else:
            invalid_years += 1

        # GDP may legitimately be null for some years.
        value = row.get("value")

        if value is None:
            null_values += 1

        elif (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
        ):
            invalid_values += 1

    # --------------------------------------------------------
    # CHECK 5: COUNTRY AND INDICATOR
    # --------------------------------------------------------

    record_check(
        checks,
        "country_and_indicator",
        len(observations) > 0
        and valid_identity == len(observations),
        (
            f"{valid_identity}/{len(observations)} observations "
            f"match India GDP ({EXPECTED_INDICATOR})."
        ),
    )

    # --------------------------------------------------------
    # CHECK 6: VALID YEARS
    # --------------------------------------------------------

    record_check(
        checks,
        "valid_years",
        len(observations) > 0 and invalid_years == 0,
        f"Invalid years: {invalid_years}",
    )

    # --------------------------------------------------------
    # CHECK 7: DUPLICATE YEARS
    # --------------------------------------------------------

    duplicate_count = (
        len(valid_years) - len(set(valid_years))
    )

    record_check(
        checks,
        "duplicate_years",
        duplicate_count == 0,
        f"Duplicate year count: {duplicate_count}",
    )

    # --------------------------------------------------------
    # CHECK 8: NUMERIC GDP VALUES
    # --------------------------------------------------------

    record_check(
        checks,
        "numeric_gdp_values",
        invalid_values == 0 and invalid_records == 0,
        (
            f"Invalid GDP values: {invalid_values}; "
            f"invalid records: {invalid_records}; "
            f"null GDP values: {null_values}."
        ),
    )

    # --------------------------------------------------------
    # SAVE REPORT AND RETURN SUMMARY
    # --------------------------------------------------------

    return save_report(
        checks,
        len(observations),
        null_values,
    )


# ============================================================
# SAVE QUALITY REPORT
# ============================================================

def save_report(
    checks: list[dict[str, str]],
    records_read: int,
    null_values: int,
) -> dict[str, Any]:
    """Write detailed results to CSV and print a summary."""

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_time = datetime.now(timezone.utc).isoformat()

    passed = sum(
        check["status"] == "PASS"
        for check in checks
    )

    failed = sum(
        check["status"] == "FAIL"
        for check in checks
    )

    total = len(checks)

    quality_score = (
        round(passed / total * 100, 2)
        if total
        else 0.0
    )

    fieldnames = [
        "report_time",
        "check_name",
        "status",
        "details",
    ]

    with REPORT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for check in checks:
            writer.writerow(
                {
                    "report_time": report_time,
                    **check,
                }
            )

    summary = {
        "records_read": records_read,
        "checks_total": total,
        "checks_passed": passed,
        "checks_failed": failed,
        "quality_score_percent": quality_score,
        "null_gdp_values": null_values,
        "overall_status": (
            "PASS" if failed == 0 else "FAIL"
        ),
        "report_path": str(
            REPORT_FILE.relative_to(PROJECT_ROOT)
        ),
    }

    # --------------------------------------------------------
    # PRINT SUMMARY
    # --------------------------------------------------------

    print("\nBRONZE DATA QUALITY SUMMARY")
    print("=" * 55)

    for check in checks:
        print(
            f"[{check['status']}] "
            f"{check['check_name']}: "
            f"{check['details']}"
        )

    print("-" * 55)
    print(f"Records read       : {records_read}")
    print(f"Checks total       : {total}")
    print(f"Checks passed      : {passed}")
    print(f"Checks failed      : {failed}")
    print(f"Quality score      : {quality_score}%")
    print(f"Overall status     : {summary['overall_status']}")
    print(f"Null GDP values    : {null_values}")
    print(f"Report             : {summary['report_path']}")
    print("=" * 55)

    return summary


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    validate_bronze_data()
