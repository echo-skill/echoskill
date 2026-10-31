import pytest


@pytest.fixture(autouse=True)
def isolate_ledger_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("LEDGER_DIR", str(tmp_path / "ledger"))
