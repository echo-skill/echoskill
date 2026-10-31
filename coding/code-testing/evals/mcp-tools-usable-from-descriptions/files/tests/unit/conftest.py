import pytest


@pytest.fixture(autouse=True)
def isolate_data(tmp_path, monkeypatch):
    monkeypatch.setenv("TINYKV_PATH", str(tmp_path / "data.json"))
