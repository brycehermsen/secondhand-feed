from __future__ import annotations

from app.domain.models.enums import DESIGN_ORDINAL, DesignLevel

DESIGN_POINTS = {
    DesignLevel.POOR: 0,
    DesignLevel.WEAK: 1,
    DesignLevel.GENERIC: 3,
    DesignLevel.SIMPLE_TASTEFUL: 5,
    DesignLevel.GREAT: 7,
    DesignLevel.AMAZING: 8,
}


def score_design(level: DesignLevel) -> tuple[int, str]:
    pts = DESIGN_POINTS[level]
    return pts, f"Design read: {level.value.replace('_', ' ')} ({DESIGN_ORDINAL[level]}/5)."
