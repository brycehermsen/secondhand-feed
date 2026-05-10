from __future__ import annotations

from dataclasses import dataclass

from app.domain.models.buyer_profile import BuyerProfile
from app.domain.models.enums import CONDITION_ORDINAL, ConditionLevel


@dataclass(frozen=True)
class ConditionNormalization:
    level: ConditionLevel
    confidence: float
    read: str


def _floor_from_profile(profile: BuyerProfile) -> ConditionLevel:
    raw_min = str(profile.condition.get("minimum", "very_good")).lower()
    mapping = {
        "new_with_tags": ConditionLevel.NEW_TAGS,
        "excellent": ConditionLevel.EXCELLENT,
        "very_good": ConditionLevel.VERY_GOOD,
        "good": ConditionLevel.GOOD,
        "fair": ConditionLevel.FAIR,
        "poor": ConditionLevel.POOR,
    }
    return mapping.get(raw_min.replace(" ", "_"), ConditionLevel.VERY_GOOD)


def normalize_condition(
    raw_condition: str | None,
    title: str,
    description: str | None,
    profile: BuyerProfile,
) -> ConditionNormalization:
    blob = f"{raw_condition or ''} {title} {description or ''}".lower()

    # Explicit ordering checks
    if "new" in blob and "tag" in blob:
        return ConditionNormalization(ConditionLevel.NEW_TAGS, 0.7, "Reads like new with tags.")
    if "excellent" in blob:
        return ConditionNormalization(ConditionLevel.EXCELLENT, 0.7, "Listed as excellent.")
    if "very good" in blob or "vg" in blob.split():
        return ConditionNormalization(ConditionLevel.VERY_GOOD, 0.65, "Listed as very good.")
    if "good" in blob and "very" not in blob:
        return ConditionNormalization(ConditionLevel.GOOD, 0.55, "Listed as good.")
    if "fair" in blob:
        return ConditionNormalization(ConditionLevel.FAIR, 0.55, "Listed as fair.")
    if "poor" in blob:
        return ConditionNormalization(ConditionLevel.POOR, 0.55, "Listed as poor.")

    floor = _floor_from_profile(profile)
    # Unknown should not assume excellence
    return ConditionNormalization(ConditionLevel.UNKNOWN, 0.25, f"Ambiguous condition; treating cautiously vs floor {floor.value}.")
