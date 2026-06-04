from pathlib import Path
import json

import pytest

import main


def test_load_watchlist(tmp_path, monkeypatch):
    watchlist_file = tmp_path / "watchlist.txt"
    watchlist_file.write_text(
        "320193\n\n789019\n1018724\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(main, "WATCHLIST_FILE", watchlist_file)

    watchlist = main.load_watchlist()

    assert watchlist == ["320193", "789019", "1018724"]


def test_save_last_run(tmp_path, monkeypatch):
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(main, "STATE_DIR", state_dir)

    last_run_file = main.save_last_run()

    assert last_run_file.exists()

    content = json.loads(last_run_file.read_text(encoding="utf-8"))
    assert "last_run" in content
    assert content["last_run"].endswith("Z")


def test_main_process_all_ciks(monkeypatch):
    called = []

    monkeypatch.setattr(main, "load_watchlist", lambda: ["320193", "789019"])
    monkeypatch.setattr(main, "save_last_run", lambda: Path("data/state/last_run.json"))

    def fake_ingest_company(cik, client=None):
        called.append(cik)

    monkeypatch.setattr(main, "ingest_company", fake_ingest_company)

    main.main()

    assert called == ["320193", "789019"]
