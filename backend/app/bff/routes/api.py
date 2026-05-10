from __future__ import annotations

from pathlib import Path

import yaml
from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import BaseModel, Field

from app.application.use_cases.run_source import execute_source_run, record_feedback, rescore_listing
from app.bff.presenters.feed_presenter import project_listing_detail
from app.config.settings import Settings
from app.deps import Deps
from app.domain.models.buyer_profile import BuyerProfile
from app.domain.models.source import SourceConfig


router = APIRouter()


def get_deps(request: Request) -> Deps:
    return request.app.state.deps


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/feed")
def api_feed(
    request: Request,
    include_oiyli: bool = False,
    include_suppressed: bool = False,
    include_hidden: bool = False,
    saved_only: bool = False,
) -> dict:
    deps = get_deps(request)
    verdicts = ["click_now", "maybe"]
    if include_oiyli:
        verdicts.append("only_if_you_love_it")
    if include_suppressed:
        verdicts.append("suppress")

    items = deps.feed_repo.list_feed_items(
        verdicts=verdicts,
        include_hidden=include_hidden,
        saved_only=saved_only,
    )
    return {"items": [i.model_dump(mode="json") for i in items]}


@router.get("/listings/{listing_id}")
def api_listing_detail(listing_id: str, request: Request) -> dict:
    deps = get_deps(request)
    listing = deps.listing_repo.get_listing(listing_id)
    evaluation = deps.evaluation_repo.get_evaluation(listing_id)
    if listing is None or evaluation is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    saved, hidden = deps.feed_repo.get_feedback_flags(listing_id)
    return project_listing_detail(listing=listing, evaluation=evaluation, is_saved=saved, is_hidden=hidden)


class FeedbackBody(BaseModel):
    action: str
    reason: str | None = None
    notes: str | None = None


@router.post("/listings/{listing_id}/feedback")
def api_feedback(listing_id: str, body: FeedbackBody, request: Request) -> dict:
    deps = get_deps(request)
    record_feedback(deps, listing_id, body.action, body.reason, body.notes)
    return {"ok": True}


@router.post("/listings/{listing_id}/rescore")
def api_rescore(listing_id: str, request: Request) -> dict:
    deps = get_deps(request)
    try:
        rescore_listing(deps, listing_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True}


@router.post("/sources/fake/run")
def api_run_fake(request: Request) -> dict:
    deps = get_deps(request)
    src = deps.source_repo.get_source("src_fake")
    if src is None:
        raise HTTPException(status_code=500, detail="Fake source not seeded")
    run = execute_source_run(deps, src)
    return run.model_dump(mode="json")


class EbayRunBody(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=20, ge=1, le=50)


@router.post("/sources/ebay/run")
def api_run_ebay(body: EbayRunBody, request: Request) -> dict:
    deps = get_deps(request)
    src = deps.source_repo.get_source("src_ebay")
    if src is None:
        raise HTTPException(status_code=500, detail="eBay source not seeded")
    cfg = deps.source_repo.get_source_config("src_ebay") | {"query": body.query, "limit": body.limit}
    deps.source_repo.set_source_config("src_ebay", cfg)
    run_cfg = src.model_copy(update={"ephemeral": {"query": body.query, "limit": body.limit}})
    run = execute_source_run(deps, run_cfg)
    return run.model_dump(mode="json")


@router.get("/runs")
def api_runs(request: Request, limit: int = 50) -> dict:
    deps = get_deps(request)
    runs = deps.run_repo.list_runs(limit)
    return {"runs": [r.model_dump(mode="json") for r in runs]}


@router.get("/profile")
def api_profile_get(request: Request) -> dict:
    settings = get_settings(request)
    path = Path(settings.profile_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Profile missing on disk")
    return {"yaml": path.read_text(encoding="utf-8")}


@router.put("/profile")
def api_profile_put(request: Request, yaml_text: str = Body(..., media_type="text/plain")) -> dict:
    settings = get_settings(request)
    data = yaml.safe_load(yaml_text)
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="YAML must map to an object")
    try:
        BuyerProfile.model_validate(data)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid profile: {exc}") from exc
    path = Path(settings.profile_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml_text, encoding="utf-8")
    return {"ok": True}

