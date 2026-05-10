from __future__ import annotations

from dataclasses import dataclass

from app.domain.models.buyer_profile import BuyerProfile
from app.domain.models.enums import BrandStatus, CONDITION_ORDINAL, ConditionLevel
from app.domain.normalization import BrandNormalization, ConditionNormalization, SizeNormalization


@dataclass(frozen=True)
class HardFilterResult:
    reject: bool
    reason: str | None = None


def _reject_terms(profile: BuyerProfile) -> list[str]:
    terms = profile.condition.get("reject_terms", [])
    return [str(t).lower() for t in terms]


def apply_hard_filters(
    *,
    title: str,
    description: str | None,
    brand: BrandNormalization,
    condition_norm: ConditionNormalization,
    size_norm: SizeNormalization,
    category_key: str,
    profile: BuyerProfile,
) -> HardFilterResult:
    blob = f"{title} {description or ''} {condition_norm.read}".lower()
    for term in _reject_terms(profile):
        if term and term in blob:
            return HardFilterResult(True, f"Hard reject term in listing text: '{term}'.")

    if brand.status is BrandStatus.EXCLUDED:
        return HardFilterResult(True, "Excluded brand.")

    floor_name = str(profile.condition.get("minimum", "very_good")).lower().replace(" ", "_")
    floor_level = {
        "new_with_tags": ConditionLevel.NEW_TAGS,
        "excellent": ConditionLevel.EXCELLENT,
        "very_good": ConditionLevel.VERY_GOOD,
        "good": ConditionLevel.GOOD,
        "fair": ConditionLevel.FAIR,
        "poor": ConditionLevel.POOR,
    }.get(floor_name, ConditionLevel.VERY_GOOD)

    if CONDITION_ORDINAL[condition_norm.level] < CONDITION_ORDINAL[floor_level] and condition_norm.level is not ConditionLevel.UNKNOWN:
        return HardFilterResult(True, f"Below minimum condition floor ({floor_level.value}).")

    tailored = any(
        k in category_key.lower()
        for k in (
            "jacket",
            "coat",
            "blazer",
            "outerwear",
            "trouser",
            "pant",
            "shirt",
        )
    )
    if not size_norm.compatible:
        if tailored:
            return HardFilterResult(True, "Size mismatch against profile for tailored category.")
        # knitwear more forgiving if cheap — handled in scoring/fit, not hard reject

    return HardFilterResult(False, None)
