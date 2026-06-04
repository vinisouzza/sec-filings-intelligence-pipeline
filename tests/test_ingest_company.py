import json
from pathlib import Path

import pytest

from ingestion import ingest_company as ingest_module


class FakeSECClient:
    def get_submissions(self, cik: str) -> dict:
        return {
            "cik": cik,
            "name": "Fake Company",
            "fillings": {"recent": {"form": ["10-K"]}}
        }
    

def test_ingest_company_saves_file(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest_module, "PROJECT_ROOT", tmp_path)

    output_file = ingest_module.ingest_company(
        "320193",
        client=FakeSECClient()
    )

    assert output_file.exists()

    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert data["cik"].zfill(10) == "0000320193"
    assert data["name"] == "Fake Company"

    expected_folder = (
        tmp_path
        / "data"
        / "raw"
        / "sec"
    )

    assert expected_folder.exists()