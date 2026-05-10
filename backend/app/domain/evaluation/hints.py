from __future__ import annotations

from app.domain.models.enums import DesignLevel, MakeQualityLevel, MaterialLevel


def parse_design_hint(raw: str | None) -> DesignLevel:
    if not raw:
        return DesignLevel.GENERIC
    key = raw.strip().lower().replace(" ", "_").replace("-", "_")
    mapping = {
        "poor": DesignLevel.POOR,
        "weak": DesignLevel.WEAK,
        "generic": DesignLevel.GENERIC,
        "simple_tasteful": DesignLevel.SIMPLE_TASTEFUL,
        "great": DesignLevel.GREAT,
        "amazing": DesignLevel.AMAZING,
    }
    return mapping.get(key, DesignLevel.GENERIC)


def parse_make_hint(raw: str | None) -> MakeQualityLevel:
    if not raw:
        return MakeQualityLevel.ORDINARY
    key = raw.strip().lower().replace(" ", "_").replace("-", "_")
    mapping = {
        "poor": MakeQualityLevel.POOR,
        "low": MakeQualityLevel.LOW,
        "ordinary": MakeQualityLevel.ORDINARY,
        "good": MakeQualityLevel.GOOD,
        "high": MakeQualityLevel.HIGH,
        "exceptional": MakeQualityLevel.EXCEPTIONAL,
    }
    return mapping.get(key, MakeQualityLevel.ORDINARY)


def parse_material_hint(raw: str | None) -> MaterialLevel:
    if not raw:
        return MaterialLevel.GOOD
    key = raw.strip().lower().replace(" ", "_").replace("-", "_")
    mapping = {
        "poor": MaterialLevel.POOR,
        "weak": MaterialLevel.WEAK,
        "good": MaterialLevel.GOOD,
        "strong": MaterialLevel.STRONG,
        "excellent": MaterialLevel.EXCELLENT,
    }
    return mapping.get(key, MaterialLevel.GOOD)
