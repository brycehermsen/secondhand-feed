from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.models import (
    Evaluation,
    FeedbackEvent,
    FeedItem,
    Listing,
    RawListingSummary,
    SourceConfig,
    SourceRun,
)


@runtime_checkable
class ListingRepository(Protocol):
    def upsert_listing(self, listing: Listing, raw_json: dict) -> None: ...

    def get_listing(self, listing_id: str) -> Listing | None: ...


@runtime_checkable
class EvaluationRepository(Protocol):
    def upsert_evaluation(self, evaluation: Evaluation, evaluated_at: str) -> None: ...

    def get_evaluation(self, listing_id: str) -> Evaluation | None: ...


@runtime_checkable
class FeedRepository(Protocol):
    def upsert_feed_item(self, item: FeedItem, last_updated_at: str) -> None: ...

    def list_feed_items(
        self,
        *,
        verdicts: list[str] | None,
        include_hidden: bool,
        saved_only: bool,
    ) -> list[FeedItem]: ...

    def get_feedback_flags(self, listing_id: str) -> tuple[bool, bool]: ...

    def update_feedback_flags(self, listing_id: str, *, is_saved: bool | None, is_hidden: bool | None) -> None: ...


@runtime_checkable
class FeedbackRepository(Protocol):
    def append_feedback(self, event: FeedbackEvent) -> None: ...


@runtime_checkable
class SourceRepository(Protocol):
    def upsert_source(self, source: SourceConfig, config_obj: dict) -> None: ...

    def get_source(self, source_id: str) -> SourceConfig | None: ...

    def get_source_config(self, source_id: str) -> dict: ...

    def set_source_config(self, source_id: str, cfg: dict) -> None: ...


@runtime_checkable
class SourceRunRepository(Protocol):
    def create_run(self, run: SourceRun) -> None: ...

    def finish_run(self, run_id: str, *, status: str, counts: dict[str, int], error: str | None) -> None: ...

    def list_runs(self, limit: int) -> list[SourceRun]: ...
