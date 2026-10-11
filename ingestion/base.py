from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

@dataclass
class IngestionResult:
    source_id: str
    status: str
    records_read: int
    output_path: str
    ingested_at: str
    error_message: str | None = None

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def save_json(data: Any, path: str | Path) -> None:
    import json
    target = Path(path)
    ensure_directory(target.parent)
    target.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
