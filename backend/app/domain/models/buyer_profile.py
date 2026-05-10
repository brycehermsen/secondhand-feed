from __future__ import annotations

from pydantic import BaseModel, Field


class PriceBand(BaseModel):
    normal_good_under: float
    special_good_under: float
    stretch_under: float


class BuyerProfile(BaseModel):
    version: int

    goal: dict[str, object]
    sizes: dict[str, dict[str, list[str]]]
    brands: dict[str, list[str]]
    categories: dict[str, list[str]]
    aesthetic: dict[str, list[str]]
    price_bands: dict[str, PriceBand]
    condition: dict[str, object]

    learned_fit_notes: dict[str, str] = Field(default_factory=dict)
    learned_brand_notes: dict[str, str] = Field(default_factory=dict)
    learned_price_notes: dict[str, str] = Field(default_factory=dict)
    examples_liked: list[str] = Field(default_factory=list)
    examples_disliked: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
