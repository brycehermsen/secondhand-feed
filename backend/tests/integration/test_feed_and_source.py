from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from app.domain.evaluation.pipeline import listing_id_from_url
from app.domain.models.enums import Verdict
from app.main import create_app


@pytest.fixture()
def temp_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db = tmp_path / "test.db"
    profile_src = Path(__file__).resolve().parents[3] / "data" / "buyer_style_profile.yaml"
    profile_dst = tmp_path / "buyer_style_profile.yaml"
    shutil.copyfile(profile_src, profile_dst)

    fixture_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "adapters"
        / "sources"
        / "fixtures"
        / "fake_listings.json"
    )

    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("PROFILE_PATH", str(profile_dst))
    monkeypatch.setenv("FAKE_FIXTURE_PATH", str(fixture_path))

    with TestClient(create_app()) as client:
        yield client, client.app.state.deps, client.app.state.settings


def test_run_fake_source_end_to_end(temp_app):
    client, _deps, _settings = temp_app
    res = client.post("/api/sources/fake/run")
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "success"

    feed = client.get("/api/feed").json()["items"]
    verdicts = {i["verdict"] for i in feed}
    assert Verdict.CLICK_NOW.value in verdicts or Verdict.MAYBE.value in verdicts

    suppressed_vis = client.get("/api/feed", params={"include_suppressed": True}).json()["items"]
    assert len(suppressed_vis) >= len(feed)


def test_feedback_hide_hides_from_default_feed(temp_app):
    client, _deps, _settings = temp_app
    client.post("/api/sources/fake/run")
    feed = client.get("/api/feed").json()["items"]
    assert feed
    lid = feed[0]["listing_id"]
    client.post(f"/api/listings/{lid}/feedback", json={"action": "hide"})
    feed2 = client.get("/api/feed").json()["items"]
    assert all(i["listing_id"] != lid for i in feed2)


def test_profile_change_affects_rescore(temp_app):
    client, _deps, settings = temp_app
    client.post("/api/sources/fake/run")
    lid = listing_id_from_url("fake://listing/001")

    prof_path = Path(settings.profile_path)
    raw = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
    raw["brands"]["excluded"].append("Drake's")
    prof_path.write_text(yaml.safe_dump(raw, sort_keys=False, allow_unicode=True), encoding="utf-8")

    client.post(f"/api/listings/{lid}/rescore")
    detail = client.get(f"/api/listings/{lid}").json()
    assert detail["verdict"] == Verdict.SUPPRESS.value
