from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models.enums import (
    DesignLevel,
    MakeQualityLevel,
    MaterialLevel,
)


class RawListingSummary(BaseModel):
    """Marketplace-shaped payload from a source connector (untrusted)."""

    marketplace: str = Field(description="e.g. fake, ebay")
    canonical_url: str
    title: str
    brand_text: str | None = None
    price_text: str | None = None
    shipping_text: str | None = None
    image_url: str | None = None
    condition_text: str | None = None
    size_text: str | None = None
    category_hint: str | None = None
    description: str | None = None
    seller_name: str | None = None
    design_level_hint: str | None = None
    make_quality_level_hint: str | None = None
    material_level_hint: str | None = None
    measurements: dict[str, str] | None = None

    model_config = {"frozen": True}


class Listing(BaseModel):
    """Persisted listing aggregate (storage-oriented; scoring stays pure functions)."""

    id: str
    source_marketplace: str | None = None
    canonical_url: str
    source_url: str | None = None
    title: str
    brand_raw: str | None = None
    brand_normalized: str | None = None
    brand_status: str | None = None
    category: str | None = None
    size_raw: str | None = None
    size_normalized: str | None = None
    condition_raw: str | None = None
    condition_normalized: str | None = None
    material: str | None = None
    price_item: float | None = None
    shipping: float | None = None
    all_in_price: float | None = None
    currency: str = "USD"
    image_url: str | None = None
    description: str | None = None
    seller_name: str | None = None
    price_text: str | None = None
    shipping_text: str | None = None
    measurements: dict[str, str] | None = None
    design_level: DesignLevel | None = None
    make_quality_level: MakeQualityLevel | None = None
    material_level: MaterialLevel | None = None

    model_config = {"frozen": True}


class EvalListingInput(BaseModel):
    """Inputs needed for evaluation (listing + connector hints)."""

    listing: Listing
    design_hint: str | None = None
    make_hint: str | None = None
    material_hint: str | None = None

    model_config = {"frozen": True}
