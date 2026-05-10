from __future__ import annotations

from pydantic import BaseModel


class FeedItem(BaseModel):
    listing_id: str
    title: str
    brand_display: str | None
    source_marketplace: str | None
    source_url: str | None
    image_url: str | None
    price_display: str
    size_display: str | None
    verdict: str
    score_total: int
    design_label: str
    make_quality_label: str
    material_label: str
    price_label: str
    fit_label: str
    condition_label: str
    brand_read: str
    why_json: list[str]
    watchouts_json: list[str]
    sort_rank: int
    is_hidden: bool = False
    is_saved: bool = False
    score_breakdown: dict[str, int] | None = None
