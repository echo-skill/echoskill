import pytest


@pytest.fixture(autouse=True)
def isolate_tally_dir(tmp_path, monkeypatch):
    """Every test gets its own TALLY_DIR; nothing touches the real home."""
    monkeypatch.setenv("TALLY_DIR", str(tmp_path / "tally"))
