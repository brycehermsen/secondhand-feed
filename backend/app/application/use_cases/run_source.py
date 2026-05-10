from __future__ import annotations

import uuid

from app.bff.presenters.feed_presenter import project_feed_item
from app.deps import Deps
from app.domain.evaluation.pipeline import evaluate_eval_input, listing_and_eval_input_from_raw, listing_id_from_url
from app.domain.models.enums import FeedbackAction, SourceRunStatus
from app.domain.models.feedback import FeedbackEvent
from app.domain.models.listing import EvalListingInput
from app.domain.models.source import SourceConfig, SourceRun


def execute_source_run(deps: Deps, source: SourceConfig) -> SourceRun:
    profile = deps.profile_store.load()
    connector = deps.connectors.get(source.source_type)
    if connector is None:
        raise RuntimeError(f"No connector registered for source_type={source.source_type}")

    run_id = str(uuid.uuid4())
    started = deps.clock.now_iso()
    deps.run_repo.create_run(
        SourceRun(
            id=run_id,
            source_id=source.id,
            status=SourceRunStatus.RUNNING.value,
            started_at=started,
            finished_at=None,
            listings_found=0,
            listings_new=0,
            listings_updated=0,
            error_message=None,
            logs_json=None,
        )
    )

    counts = {"found": 0, "new": 0, "updated": 0}
    try:
        raws = connector.fetch(source)
        counts["found"] = len(raws)
        now = deps.clock.now_iso()
        for raw in raws:
            lid = listing_id_from_url(raw.canonical_url)
            existed = deps.listing_repo.get_listing(lid) is not None
            inp = listing_and_eval_input_from_raw(raw, lid, profile)
            deps.listing_repo.upsert_listing(inp.listing, raw.model_dump(mode="json"))
            evaluation = evaluate_eval_input(inp, profile)
            deps.evaluation_repo.upsert_evaluation(evaluation, now)
            saved, hidden = deps.feed_repo.get_feedback_flags(lid)
            item = project_feed_item(inp.listing, evaluation, is_saved=saved, is_hidden=hidden)
            deps.feed_repo.upsert_feed_item(item, now)
            if existed:
                counts["updated"] += 1
            else:
                counts["new"] += 1

        deps.run_repo.finish_run(run_id, status=SourceRunStatus.SUCCESS.value, counts=counts, error=None)
        return SourceRun(
            id=run_id,
            source_id=source.id,
            status=SourceRunStatus.SUCCESS.value,
            started_at=started,
            finished_at=deps.clock.now_iso(),
            listings_found=counts["found"],
            listings_new=counts["new"],
            listings_updated=counts["updated"],
            error_message=None,
            logs_json=None,
        )
    except Exception as exc:  # noqa: BLE001 - surfaced to UI/logs
        deps.run_repo.finish_run(
            run_id,
            status=SourceRunStatus.FAILED.value,
            counts=counts,
            error=str(exc),
        )
        return SourceRun(
            id=run_id,
            source_id=source.id,
            status=SourceRunStatus.FAILED.value,
            started_at=started,
            finished_at=deps.clock.now_iso(),
            listings_found=counts["found"],
            listings_new=counts["new"],
            listings_updated=counts["updated"],
            error_message=str(exc),
            logs_json=None,
        )


def record_feedback(deps: Deps, listing_id: str, action: str, reason: str | None, notes: str | None) -> None:
    act = FeedbackAction(action)
    event = FeedbackEvent(
        id=str(uuid.uuid4()),
        listing_id=listing_id,
        action=act.value,
        reason=reason,
        notes=notes,
        created_at=deps.clock.now_iso(),
    )
    deps.feedback_repo.append_feedback(event)

    saved: bool | None = None
    hidden: bool | None = None
    match act:
        case FeedbackAction.SAVE:
            saved = True
        case FeedbackAction.UNSAVE:
            saved = False
        case FeedbackAction.HIDE:
            hidden = True
        case FeedbackAction.UNHIDE:
            hidden = False

    deps.feed_repo.update_feedback_flags(listing_id, is_saved=saved, is_hidden=hidden)


def rescore_listing(deps: Deps, listing_id: str) -> None:
    listing = deps.listing_repo.get_listing(listing_id)
    if listing is None:
        raise ValueError("Listing not found")

    profile = deps.profile_store.load()
    inp = EvalListingInput(listing=listing)
    evaluation = evaluate_eval_input(inp, profile)
    now = deps.clock.now_iso()
    deps.evaluation_repo.upsert_evaluation(evaluation, now)
    saved, hidden = deps.feed_repo.get_feedback_flags(listing_id)
    item = project_feed_item(listing, evaluation, is_saved=saved, is_hidden=hidden)
    deps.feed_repo.upsert_feed_item(item, now)
