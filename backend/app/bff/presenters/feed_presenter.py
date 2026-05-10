from __future__ import annotations

from app.domain.models.enums import DesignLevel, FitRead, MakeQualityLevel, MaterialLevel, PriceRead, Verdict
from app.domain.models.evaluation import Evaluation
from app.domain.models.feed_item import FeedItem
from app.domain.models.listing import Listing


def _money(listing: Listing) -> str:
    if listing.all_in_price is None:
        return "Price unknown"
    return f"{listing.currency} {listing.all_in_price:.0f}"


def human_design(level: DesignLevel | None) -> str:
    if level is None:
        return "Unknown"
    return {
        DesignLevel.POOR: "Poor design",
        DesignLevel.WEAK: "Weak design",
        DesignLevel.GENERIC: "Generic",
        DesignLevel.SIMPLE_TASTEFUL: "Simple & tasteful",
        DesignLevel.GREAT: "Great design",
        DesignLevel.AMAZING: "Amazing design",
    }[level]


def human_make(level: MakeQualityLevel | None) -> str:
    if level is None:
        return "Unknown"
    return {
        MakeQualityLevel.POOR: "Poor make",
        MakeQualityLevel.LOW: "Low make",
        MakeQualityLevel.ORDINARY: "Ordinary make",
        MakeQualityLevel.GOOD: "Good make",
        MakeQualityLevel.HIGH: "High make",
        MakeQualityLevel.EXCEPTIONAL: "Exceptional make",
    }[level]


def human_material(level: MaterialLevel | None) -> str:
    if level is None:
        return "Unknown"
    return {
        MaterialLevel.POOR: "Poor material",
        MaterialLevel.WEAK: "Weak material",
        MaterialLevel.GOOD: "Good material",
        MaterialLevel.STRONG: "Strong material",
        MaterialLevel.EXCELLENT: "Excellent material",
    }[level]


def human_price_read(read: str) -> str:
    try:
        pr = PriceRead(read)
    except ValueError:
        return read
    return {
        PriceRead.EXCELLENT: "Excellent price",
        PriceRead.GOOD: "Good price",
        PriceRead.FAIR: "Fair price",
        PriceRead.STRETCH: "Stretch price",
        PriceRead.BAD: "Bad price / unclear",
    }[pr]


def human_fit_read(read: str) -> str:
    try:
        fr = FitRead(read)
    except ValueError:
        return read.replace("_", " ").title()
    return {
        FitRead.GOOD: "Good fit vs profile",
        FitRead.UNCERTAIN: "Uncertain fit",
        FitRead.BAD: "Poor fit vs profile",
    }[fr]


def human_verdict(v: str) -> str:
    try:
        verdict = Verdict(v)
    except ValueError:
        return v
    return {
        Verdict.CLICK_NOW: "Click now",
        Verdict.MAYBE: "Maybe",
        Verdict.ONLY_IF_YOU_LOVE_IT: "Only if you love it",
        Verdict.SUPPRESS: "Suppress",
    }[verdict]


def project_feed_item(
    listing: Listing,
    evaluation: Evaluation,
    *,
    is_saved: bool,
    is_hidden: bool,
) -> FeedItem:
    why = evaluation.why[:3]
    watch = evaluation.watchouts[:1]

    return FeedItem(
        listing_id=listing.id,
        title=listing.title,
        brand_display=listing.brand_normalized,
        source_marketplace=listing.source_marketplace,
        source_url=listing.source_url or listing.canonical_url,
        image_url=listing.image_url,
        price_display=_money(listing),
        size_display=listing.size_raw or listing.size_normalized,
        verdict=evaluation.verdict.value,
        score_total=evaluation.score.total,
        design_label=human_design(listing.design_level),
        make_quality_label=human_make(listing.make_quality_level),
        material_label=human_material(listing.material_level),
        price_label=human_price_read(evaluation.price_read),
        fit_label=human_fit_read(evaluation.fit_read),
        condition_label=evaluation.condition_read,
        brand_read=evaluation.brand_read,
        why_json=why,
        watchouts_json=watch,
        sort_rank=evaluation.score.total,
        is_hidden=is_hidden,
        is_saved=is_saved,
        score_breakdown=None,
    )


def project_listing_detail(
    *,
    listing: Listing,
    evaluation: Evaluation,
    is_saved: bool,
    is_hidden: bool,
) -> dict:
    s = evaluation.score
    return {
        "listing_id": listing.id,
        "title": listing.title,
        "brand": listing.brand_normalized,
        "source_marketplace": listing.source_marketplace,
        "source_url": listing.source_url or listing.canonical_url,
        "image_url": listing.image_url,
        "price_display": _money(listing),
        "size_display": listing.size_raw or listing.size_normalized,
        "verdict": evaluation.verdict.value,
        "verdict_label": human_verdict(evaluation.verdict.value),
        "score_total": s.total,
        "score_breakdown": {
            "brand": s.brand,
            "category": s.category,
            "design": s.design,
            "quality_of_make": s.quality_of_make,
            "material": s.material,
            "price": s.price,
            "fit": s.fit,
            "condition": s.condition,
        },
        "reads": {
            "design": evaluation.design_read,
            "make_quality": evaluation.make_quality_read,
            "material": evaluation.material_read,
            "brand": evaluation.brand_read,
            "price": evaluation.price_read,
            "fit": evaluation.fit_read,
            "condition": evaluation.condition_read,
        },
        "labels": {
            "design": human_design(listing.design_level),
            "make_quality": human_make(listing.make_quality_level),
            "material": human_material(listing.material_level),
            "price": human_price_read(evaluation.price_read),
        },
        "why": evaluation.why,
        "watchouts": evaluation.watchouts,
        "seller_question": evaluation.seller_question,
        "hard_reject_reason": evaluation.hard_reject_reason,
        "is_saved": is_saved,
        "is_hidden": is_hidden,
        "measurements": listing.measurements or {},
    }
