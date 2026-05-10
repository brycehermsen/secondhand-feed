from __future__ import annotations

from enum import StrEnum


class Verdict(StrEnum):
    CLICK_NOW = "click_now"
    MAYBE = "maybe"
    ONLY_IF_YOU_LOVE_IT = "only_if_you_love_it"
    SUPPRESS = "suppress"


class BrandStatus(StrEnum):
    TARGET = "target"
    CREDIBLE_NON_TARGET = "credible_non_target"
    REPUTATION_WATCHLIST = "reputation_watchlist"
    EXCLUDED = "excluded"
    UNKNOWN = "unknown"


class DesignLevel(StrEnum):
    POOR = "poor"
    WEAK = "weak"
    GENERIC = "generic"
    SIMPLE_TASTEFUL = "simple_tasteful"
    GREAT = "great"
    AMAZING = "amazing"


class MakeQualityLevel(StrEnum):
    POOR = "poor"
    LOW = "low"
    ORDINARY = "ordinary"
    GOOD = "good"
    HIGH = "high"
    EXCEPTIONAL = "exceptional"


class MaterialLevel(StrEnum):
    POOR = "poor"
    WEAK = "weak"
    GOOD = "good"
    STRONG = "strong"
    EXCELLENT = "excellent"


class ConditionLevel(StrEnum):
    NEW_TAGS = "new_with_tags"
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"


class PriceRead(StrEnum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    STRETCH = "stretch"
    BAD = "bad"


class FitRead(StrEnum):
    GOOD = "good"
    UNCERTAIN = "uncertain"
    BAD = "bad"


class FeedbackAction(StrEnum):
    SAVE = "save"
    HIDE = "hide"
    UNSAVE = "unsave"
    UNHIDE = "unhide"


class SourceRunStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


DESIGN_ORDINAL = {
    DesignLevel.POOR: 0,
    DesignLevel.WEAK: 1,
    DesignLevel.GENERIC: 2,
    DesignLevel.SIMPLE_TASTEFUL: 3,
    DesignLevel.GREAT: 4,
    DesignLevel.AMAZING: 5,
}

MAKE_ORDINAL = {
    MakeQualityLevel.POOR: 0,
    MakeQualityLevel.LOW: 1,
    MakeQualityLevel.ORDINARY: 2,
    MakeQualityLevel.GOOD: 3,
    MakeQualityLevel.HIGH: 4,
    MakeQualityLevel.EXCEPTIONAL: 5,
}

MATERIAL_ORDINAL = {
    MaterialLevel.POOR: 0,
    MaterialLevel.WEAK: 1,
    MaterialLevel.GOOD: 2,
    MaterialLevel.STRONG: 3,
    MaterialLevel.EXCELLENT: 4,
}

CONDITION_ORDINAL = {
    ConditionLevel.NEW_TAGS: 6,
    ConditionLevel.EXCELLENT: 5,
    ConditionLevel.VERY_GOOD: 4,
    ConditionLevel.GOOD: 3,
    ConditionLevel.FAIR: 2,
    ConditionLevel.POOR: 1,
    ConditionLevel.UNKNOWN: 0,
}
