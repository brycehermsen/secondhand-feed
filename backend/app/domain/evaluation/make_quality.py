from __future__ import annotations

from app.domain.models.enums import MAKE_ORDINAL, MakeQualityLevel

MAKE_POINTS = {
    MakeQualityLevel.POOR: 0,
    MakeQualityLevel.LOW: 1,
    MakeQualityLevel.ORDINARY: 2,
    MakeQualityLevel.GOOD: 4,
    MakeQualityLevel.HIGH: 5,
    MakeQualityLevel.EXCEPTIONAL: 6,
}


def score_make_quality(level: MakeQualityLevel) -> tuple[int, str]:
    pts = MAKE_POINTS[level]
    return pts, f"Make quality read: {level.value} ({MAKE_ORDINAL[level]}/5)."
