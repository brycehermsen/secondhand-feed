from __future__ import annotations

from app.domain.models.enums import MATERIAL_ORDINAL, MaterialLevel

MATERIAL_POINTS = {
    MaterialLevel.POOR: 0,
    MaterialLevel.WEAK: 1,
    MaterialLevel.GOOD: 2,
    MaterialLevel.STRONG: 3,
    MaterialLevel.EXCELLENT: 4,
}


def score_material(level: MaterialLevel) -> tuple[int, str]:
    pts = MATERIAL_POINTS[level]
    return pts, f"Material read: {level.value} ({MATERIAL_ORDINAL[level]}/4)."
