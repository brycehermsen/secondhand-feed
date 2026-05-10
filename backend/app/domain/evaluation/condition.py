from __future__ import annotations

from app.domain.models.buyer_profile import BuyerProfile
from app.domain.models.enums import CONDITION_ORDINAL, ConditionLevel
from app.domain.normalization import ConditionNormalization


def _floor_level(profile: BuyerProfile) -> ConditionLevel:
    raw_min = str(profile.condition.get("minimum", "very_good")).lower().replace(" ", "_")
    mapping = {
        "new_with_tags": ConditionLevel.NEW_TAGS,
        "excellent": ConditionLevel.EXCELLENT,
        "very_good": ConditionLevel.VERY_GOOD,
        "good": ConditionLevel.GOOD,
        "fair": ConditionLevel.FAIR,
        "poor": ConditionLevel.POOR,
    }
    return mapping.get(raw_min, ConditionLevel.VERY_GOOD)


def score_condition(norm: ConditionNormalization, profile: BuyerProfile) -> tuple[int, str]:
    floor = _floor_level(profile)
    # Points reward condition quality, penalize unknown slightly
    base_map = {
        ConditionLevel.NEW_TAGS: 5,
        ConditionLevel.EXCELLENT: 5,
        ConditionLevel.VERY_GOOD: 4,
        ConditionLevel.GOOD: 3,
        ConditionLevel.FAIR: 2,
        ConditionLevel.POOR: 0,
        ConditionLevel.UNKNOWN: 2,
    }
    pts = base_map[norm.level]
    if CONDITION_ORDINAL[norm.level] < CONDITION_ORDINAL[floor] and norm.level is not ConditionLevel.UNKNOWN:
        pts = min(pts, 1)
    read = f"Condition read: {norm.level.value.replace('_', ' ')} vs floor {floor.value}."
    return pts, read
