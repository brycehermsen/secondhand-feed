from __future__ import annotations

from app.domain.normalization import CategoryNormalization


def score_category(cat: CategoryNormalization) -> tuple[int, str]:
    match cat.priority:
        case "high":
            return 4, "High-priority category."
        case "medium":
            return 3, "Medium-priority category."
        case _:
            return 1, "Low-priority or unclear category."
