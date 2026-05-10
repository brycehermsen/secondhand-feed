from __future__ import annotations

from app.domain.models.enums import MaterialLevel, PriceRead
from app.domain.models.evaluation import ScoreBreakdown
from app.domain.normalization import BrandNormalization


def clamp_total(parts: dict[str, int]) -> ScoreBreakdown:
    total = sum(parts.values())
    total = max(0, min(50, total))
    return ScoreBreakdown(
        brand=parts["brand"],
        category=parts["category"],
        design=parts["design"],
        quality_of_make=parts["quality_of_make"],
        material=parts["material"],
        price=parts["price"],
        fit=parts["fit"],
        condition=parts["condition"],
        total=total,
    )


def cheap_boost_material_domination(
    brand: BrandNormalization,
    parts: dict[str, int],
    price_read: PriceRead,
    material: MaterialLevel,
) -> dict[str, int]:
    """Prevent material from rescuing a weak overall story when price isn't excellent."""
    if material.value in ("strong", "excellent") and parts["design"] <= 3 and price_read in (PriceRead.BAD, PriceRead.STRETCH):
        parts["material"] = min(parts["material"], 2)
    if brand.status.value == "unknown" and price_read is PriceRead.FAIR and parts["design"] <= 3 and parts["quality_of_make"] <= 3:
        parts["brand"] = min(parts["brand"], 2)
    return parts
