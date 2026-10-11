from ingestion.base import ensure_directory, utc_now

def test_utc_now_is_iso_string():
    value = utc_now()
    assert "T" in value

def test_ensure_directory(tmp_path):
    target = ensure_directory(tmp_path / "bronze")
    assert target.exists()
    assert target.is_dir()
