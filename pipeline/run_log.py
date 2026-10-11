from __future__ import annotations

import csv
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOG_DIR = (
    PROJECT_ROOT
    / "data"
    / "pipeline_logs"
)

LOG_FILE = LOG_DIR / "pipeline_run_log.csv"


# ---------------------------------------------------------
# PIPELINE RUN MODEL
# ---------------------------------------------------------

@dataclass
class PipelineRun:
    run_id: str
    source_id: str
    source_name: str
    start_time: str
    end_time: str
    records_read: int
    records_written: int
    status: str
    error_message: Optional[str]
    processing_time_seconds: float


# ---------------------------------------------------------
# RUN ID
# ---------------------------------------------------------

def create_run_id(source_id: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    return f"{source_id}_{timestamp}"


# ---------------------------------------------------------
# WRITE PIPELINE LOG
# ---------------------------------------------------------

def write_pipeline_log(run: PipelineRun) -> None:

    # Create folder automatically
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_exists = LOG_FILE.exists()

    fieldnames = [
        "run_id",
        "source_id",
        "source_name",
        "start_time",
        "end_time",
        "records_read",
        "records_written",
        "status",
        "error_message",
        "processing_time_seconds",
    ]

    with LOG_FILE.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            asdict(run)
        )


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        f"Pipeline log location: {LOG_FILE}"
    )