from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from app.adapters.db.sqlite_store import (
    SqliteEvaluationRepository,
    SqliteFeedbackRepository,
    SqliteFeedRepository,
    SqliteListingRepository,
    SqliteSourceRepository,
    SqliteSourceRunRepository,
)
from app.adapters.profile.yaml_profile_store import YamlProfileStore
from app.adapters.sources.ebay_connector import EbayBrowseConnector
from app.adapters.sources.fake_connector import FakeMarketplaceConnector
from app.adapters.time.system_clock import SystemClock
from app.config.settings import Settings
from app.ports.clock import Clock
from app.ports.repositories import (
    EvaluationRepository,
    FeedbackRepository,
    FeedRepository,
    ListingRepository,
    SourceRepository,
    SourceRunRepository,
)
from app.ports.source_connector import ProfileStore, SourceConnector


@dataclass
class Deps:
    conn: sqlite3.Connection
    clock: Clock
    profile_store: ProfileStore
    listing_repo: ListingRepository
    evaluation_repo: EvaluationRepository
    feed_repo: FeedRepository
    feedback_repo: FeedbackRepository
    source_repo: SourceRepository
    run_repo: SourceRunRepository
    connectors: dict[str, SourceConnector]


def build_deps(conn: sqlite3.Connection, settings: Settings) -> Deps:
    fixture_path = settings.resolved_fixture_path()
    fake = FakeMarketplaceConnector(fixture_path)
    ebay = EbayBrowseConnector(
        client_id=settings.ebay_client_id,
        client_secret=settings.ebay_client_secret,
        marketplace_id=settings.ebay_marketplace_id,
    )
    connectors: dict[str, SourceConnector] = {
        fake.source_type: fake,
        ebay.source_type: ebay,
    }
    return Deps(
        conn=conn,
        clock=SystemClock(),
        profile_store=YamlProfileStore(Path(settings.profile_path)),
        listing_repo=SqliteListingRepository(conn),
        evaluation_repo=SqliteEvaluationRepository(conn),
        feed_repo=SqliteFeedRepository(conn),
        feedback_repo=SqliteFeedbackRepository(conn),
        source_repo=SqliteSourceRepository(conn),
        run_repo=SqliteSourceRunRepository(conn),
        connectors=connectors,
    )
