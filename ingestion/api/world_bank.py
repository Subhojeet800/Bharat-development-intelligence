from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from ingestion.base import IngestionResult
from pipeline.run_log import (
    PipelineRun,
    create_run_id,
    write_pipeline_log,
)


SOURCE_ID = "WB001"
SOURCE_NAME = "World Bank Indicators"

API_URL = (
    "https://api.worldbank.org/v2/"
    "country/IND/indicator/NY.GDP.MKTP.CD"
    "?format=json&per_page=100"
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "world_bank"
    / "india_gdp.json"
)


def utc_now() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def ingest_world_bank() -> IngestionResult:
    """Fetch India GDP data from World Bank and save it to Bronze."""

    start_time = utc_now()
    start_perf = time.perf_counter()

    run_id = create_run_id(SOURCE_ID)

    records_read = 0
    records_written = 0

    try:
        response = requests.get(
            API_URL,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list) or len(data) < 2:
            raise ValueError(
                "Unexpected World Bank API response format."
            )

        observations = data[1]

        if not isinstance(observations, list):
            raise ValueError(
                "World Bank observations are not a list."
            )

        records_read = len(observations)

        # Create Bronze directory
        OUTPUT_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Write raw API response
        with OUTPUT_PATH.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
            )

        records_written = records_read

        end_time = utc_now()
        processing_time = time.perf_counter() - start_perf

        # Create pipeline audit record
        pipeline_run = PipelineRun(
            run_id=run_id,
            source_id=SOURCE_ID,
            source_name=SOURCE_NAME,
            start_time=start_time,
            end_time=end_time,
            records_read=records_read,
            records_written=records_written,
            status="SUCCESS",
            error_message=None,
            processing_time_seconds=round(
                processing_time,
                3,
            ),
        )

        # Write audit record
        write_pipeline_log(pipeline_run)

        return IngestionResult(
            source_id=SOURCE_ID,
            status="SUCCESS",
            records_read=records_read,
            output_path=str(
                OUTPUT_PATH.relative_to(PROJECT_ROOT)
            ),
            ingested_at=end_time,
            error_message=None,
        )

    except Exception as exc:

        end_time = utc_now()
        processing_time = time.perf_counter() - start_perf

        # Write failed pipeline run to audit log
        pipeline_run = PipelineRun(
            run_id=run_id,
            source_id=SOURCE_ID,
            source_name=SOURCE_NAME,
            start_time=start_time,
            end_time=end_time,
            records_read=records_read,
            records_written=records_written,
            status="FAILED",
            error_message=str(exc),
            processing_time_seconds=round(
                processing_time,
                3,
            ),
        )

        write_pipeline_log(pipeline_run)

        return IngestionResult(
            source_id=SOURCE_ID,
            status="FAILED",
            records_read=records_read,
            output_path=None,
            ingested_at=end_time,
            error_message=str(exc),
        )


if __name__ == "__main__":
    result = ingest_world_bank()
    print(result)