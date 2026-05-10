from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models.enums import Verdict


class ScoreBreakdown(BaseModel):
    brand: int = Field(ge=0, le=8)
    category: int = Field(ge=0, le=4)
    design: int = Field(ge=0, le=8)
    quality_of_make: int = Field(ge=0, le=6)
    material: int = Field(ge=0, le=4)
    price: int = Field(ge=0, le=10)
    fit: int = Field(ge=0, le=5)
    condition: int = Field(ge=0, le=5)
    total: int = Field(ge=0, le=50)

    model_config = {"frozen": True}


class Evaluation(BaseModel):
    listing_id: str
    verdict: Verdict
    score: ScoreBreakdown
    price_read: str
    fit_read: str
    condition_read: str
    design_read: str
    make_quality_read: str
    material_read: str
    brand_read: str
    why: list[str]
    watchouts: list[str]
    seller_question: str | None = None
    hard_reject_reason: str | None = None

    model_config = {"frozen": True}
