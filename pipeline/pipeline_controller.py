from __future__ import annotations

import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Callable


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_REGISTRY = (
    PROJECT_ROOT
    / "data_sources"
    / "source_registry.csv"
)

PIPELINE_LOG = (
    PROJECT_ROOT
    / "data"
    / "pipeline_logs"
    / "pipeline_run_log.csv"
)


# ============================================================
# INGESTION FUNCTIONS
# ============================================================

def run_world_bank() -> None:
    """
    Run the World Bank ingestion pipeline.
    """

    from ingestion.api.world_bank import ingest_world_bank

    result = ingest_world_bank()

    print(result)

    if result.status != "SUCCESS":
        raise RuntimeError(
            f"World Bank ingestion failed: {result.error_message}"
        )


# ============================================================
# SOURCE REGISTRY → INGESTION FUNCTION MAPPING
# ============================================================

INGESTION_FUNCTIONS: dict[str, Callable[[], None]] = {
    "WB001": run_world_bank,
}


# ============================================================
# READ SOURCE REGISTRY
# ============================================================

def load_source_registry() -> list[dict[str, str]]:
    """
    Load active sources from source_registry.csv.
    """

    if not SOURCE_REGISTRY.exists():
        raise FileNotFoundError(
            f"Source registry not found: {SOURCE_REGISTRY}"
        )

    with SOURCE_REGISTRY.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        return [
            row
            for row in reader
            if row.get("active_flag", "true").strip().lower()
            in {"true", "1", "yes", "y"}
        ]


# ============================================================
# READ PIPELINE HISTORY
# ============================================================

def get_last_successful_run(
    source_id: str,
) -> datetime | None:
    """
    Find the most recent successful pipeline execution
    for a given source.
    """

    if not PIPELINE_LOG.exists():
        return None

    latest_run: datetime | None = None

    with PIPELINE_LOG.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row.get("source_id") != source_id:
                continue

            if row.get("status") != "SUCCESS":
                continue

            end_time = row.get("end_time")

            if not end_time:
                continue

            try:
                run_time = datetime.fromisoformat(
                    end_time
                )

                if latest_run is None or run_time > latest_run:
                    latest_run = run_time

            except ValueError:
                continue

    return latest_run


# ============================================================
# FREQUENCY LOGIC
# ============================================================

def frequency_to_timedelta(
    frequency: str,
) -> timedelta | None:
    """
    Convert source frequency into an approximate
    scheduling interval.

    Note:
    This is an MVP scheduler. Exact calendar scheduling
    will later be handled by Azure Data Factory.
    """

    frequency = frequency.strip().lower()

    frequency_map = {
        "daily": timedelta(days=1),
        "weekly": timedelta(days=7),
        "monthly": timedelta(days=30),
        "quarterly": timedelta(days=90),
        "annual": timedelta(days=365),
        "yearly": timedelta(days=365),
    }

    return frequency_map.get(frequency)


def is_source_due(
    source: dict[str, str],
) -> bool:
    """
    Determine whether a source should be executed.
    """

    source_id = source.get("source_id", "").strip()
    frequency = source.get("frequency", "").strip()

    last_run = get_last_successful_run(source_id)

    # Never successfully executed → source is due
    if last_run is None:
        return True

    interval = frequency_to_timedelta(frequency)

    # Unknown/variable/periodic frequency:
    # leave it for manual execution for now.
    if interval is None:
        return False

    now = datetime.now(timezone.utc)

    next_due_time = last_run + interval

    return now >= next_due_time


# ============================================================
# RUN ONE SOURCE
# ============================================================

def run_source(
    source: dict[str, str],
) -> None:

    source_id = source.get("source_id", "").strip()
    source_name = source.get("source_name", "").strip()

    print()
    print("=" * 70)
    print(f"Source ID   : {source_id}")
    print(f"Source Name : {source_name}")
    print("=" * 70)

    ingestion_function = INGESTION_FUNCTIONS.get(
        source_id
    )

    if ingestion_function is None:

        print(
            f"SKIPPED: No ingestion function registered "
            f"for {source_id}"
        )

        return

    print("Starting ingestion...")

    ingestion_function()

    print("Ingestion completed.")


# ============================================================
# MAIN CONTROLLER
# ============================================================

def run_pipeline(
    force_run: bool = False,
) -> None:
    """
    Run all sources that are due.

    force_run=True executes all registered sources,
    regardless of their frequency.
    """

    print()
    print("=" * 70)
    print("BHARAT DEVELOPMENT INTELLIGENCE")
    print("METADATA-DRIVEN PIPELINE CONTROLLER")
    print("=" * 70)

    sources = load_source_registry()

    print()
    print(f"Active sources found: {len(sources)}")

    executed = 0
    skipped = 0

    for source in sources:

        source_id = source.get(
            "source_id",
            "",
        ).strip()

        source_name = source.get(
            "source_name",
            "",
        ).strip()

        if source_id not in INGESTION_FUNCTIONS:

            print(
                f"[SKIP] {source_id} - "
                f"{source_name} - "
                f"No ingestion adapter yet."
            )

            skipped += 1
            continue

        if force_run:

            print(
                f"[FORCE] {source_id} - "
                f"{source_name}"
            )

            run_source(source)

            executed += 1
            continue

        if is_source_due(source):

            print(
                f"[DUE] {source_id} - "
                f"{source_name}"
            )

            run_source(source)

            executed += 1

        else:

            print(
                f"[NOT DUE] {source_id} - "
                f"{source_name}"
            )

            skipped += 1

    print()
    print("=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    print(f"Executed : {executed}")
    print(f"Skipped  : {skipped}")
    print("=" * 70)


# ============================================================
# COMMAND LINE ENTRY POINT
# ============================================================

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Bharat Development Intelligence "
            "Pipeline Controller"
        )
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Run all registered ingestion sources.",
    )

    args = parser.parse_args()

    run_pipeline(
        force_run=args.force
    )