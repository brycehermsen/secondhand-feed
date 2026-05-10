from __future__ import annotations

import json
from pathlib import Path

from app.domain.models.listing import RawListingSummary
from app.domain.models.source import SourceConfig
from app.ports.source_connector import SourceConnector


class FakeMarketplaceConnector(SourceConnector):
    """Loads fixture listings; does not read buyer profile or score."""

    source_type = "fake"

    def __init__(self, default_fixture: Path):
        self.default_fixture = default_fixture

    def fetch(self, config: SourceConfig) -> list[RawListingSummary]:
        _ = config
        path = self.default_fixture
        rows = json.loads(path.read_text(encoding="utf-8"))
        out: list[RawListingSummary] = []
        for row in rows:
            url = row.get("url") or row.get("canonical_url")
            if not url:
                raise ValueError("Fixture listing missing url/canonical_url")
            out.append(
                RawListingSummary(
                    marketplace=str(row.get("source", "fake")),
                    canonical_url=str(url),
                    title=str(row["title"]),
                    brand_text=row.get("brand_text"),
                    price_text=row.get("price_text"),
                    shipping_text=row.get("shipping_text"),
                    image_url=row.get("image_url"),
                    condition_text=row.get("condition_text"),
                    size_text=row.get("size_text"),
                    category_hint=row.get("category_hint"),
                    description=row.get("description"),
                    seller_name=row.get("seller_name"),
                    design_level_hint=row.get("design_level_hint"),
                    make_quality_level_hint=row.get("make_quality_level_hint"),
                    material_level_hint=row.get("material_level_hint"),
                    measurements=row.get("measurements"),
                )
            )
        return out
