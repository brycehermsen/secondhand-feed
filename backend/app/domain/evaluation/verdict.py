from __future__ import annotations

from app.domain.models.buyer_profile import BuyerProfile
from app.domain.models.enums import (
    DESIGN_ORDINAL,
    MAKE_ORDINAL,
    BrandStatus,
    DesignLevel,
    MakeQualityLevel,
    PriceRead,
    Verdict,
)


def _normal_floor(profile: BuyerProfile, category_key: str) -> float:
    ck = category_key.lower()
    bands = profile.price_bands
    if "knit" in ck:
        b = bands["knitwear"]
    elif "chore" in ck or "overshirt" in ck:
        b = bands["overshirts_chore_coats"]
    elif "casual jacket" in ck:
        b = bands["casual_jackets"]
    elif "outer" in ck or "coat" in ck:
        b = bands["outerwear"]
    elif "shirt" in ck:
        b = bands["shirts"]
    elif "trouser" in ck or "denim" in ck or "pant" in ck:
        b = bands["trousers"]
    elif "shoe" in ck or "boot" in ck:
        b = bands["shoes"]
    else:
        b = bands["shirts"]
    return float(b.normal_good_under)


def is_very_cheap(all_in: float | None, profile: BuyerProfile, category_key: str) -> bool:
    if all_in is None:
        return False
    return all_in <= 0.55 * _normal_floor(profile, category_key)


def verdict_from_total(total: int) -> Verdict:
    if total >= 40:
        return Verdict.CLICK_NOW
    if total >= 32:
        return Verdict.MAYBE
    if total >= 25:
        return Verdict.ONLY_IF_YOU_LOVE_IT
    return Verdict.SUPPRESS


def surface_verdict_override(
    *,
    design: DesignLevel,
    make: MakeQualityLevel,
    all_in: float | None,
    profile: BuyerProfile,
    category_key: str,
    brand_status: BrandStatus,
    price_read: PriceRead,
    total_before_clamp: int,
) -> Verdict | None:
    """Business rules that suppress noisy listings regardless of partial totals."""

    d = DESIGN_ORDINAL[design]
    m = MAKE_ORDINAL[make]

    if design is DesignLevel.POOR:
        return Verdict.SUPPRESS

    if d <= 1 and not is_very_cheap(all_in, profile, category_key):
        return Verdict.SUPPRESS

    if d == 2 and m <= 2 and not is_very_cheap(all_in, profile, category_key):
        return Verdict.SUPPRESS

    # Generic discovery story: unknown brand + fair-ish price + mediocre design/make
    if brand_status is BrandStatus.UNKNOWN and price_read in (PriceRead.FAIR, PriceRead.STRETCH, PriceRead.BAD):
        if d <= 2 and m <= 2:
            return Verdict.SUPPRESS

    # Skeptical of amazing-looking listings with poor make unless very cheap
    if d >= 4 and m <= 1 and not is_very_cheap(all_in, profile, category_key):
        return Verdict.ONLY_IF_YOU_LOVE_IT if total_before_clamp >= 28 else Verdict.SUPPRESS

    return None
