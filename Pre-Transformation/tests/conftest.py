import pytest

@pytest.fixture(autouse=True)
def clean_local_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
