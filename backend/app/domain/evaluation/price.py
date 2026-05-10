from __future__ import annotations

from app.domain.models.buyer_profile import BuyerProfile, PriceBand
from app.domain.models.enums import DesignLevel, MakeQualityLevel, MaterialLevel, PriceRead


def _band_for_category(category_key: str, profile: BuyerProfile) -> PriceBand:
    ck = category_key.lower()
    bands = profile.price_bands
    if "knit" in ck:
        return bands["knitwear"]
    if "chore" in ck or "overshirt" in ck:
        return bands["overshirts_chore_coats"]
    if "casual jacket" in ck or ck.strip() == "jackets":
        return bands["casual_jackets"]
    if "outer" in ck or "coat" in ck:
        return bands["outerwear"]
    if "shirt" in ck:
        return bands["shirts"]
    if "trouser" in ck or "denim" in ck or "pant" in ck:
        return bands["trousers"]
    if "shoe" in ck or "boot" in ck or "loafer" in ck:
        return bands["shoes"]
    # Default to shirts bucket as conservative baseline
    return bands["shirts"]


def _is_plain_cashmere(title: str, description: str | None) -> bool:
    blob = f"{title} {description or ''}".lower()
    return "cashmere" in blob and "pattern" not in blob and "fair isle" not in blob


def score_price(
    *,
    all_in: float | None,
    category_key: str,
    design: DesignLevel,
    make: MakeQualityLevel,
    material: MaterialLevel,
    title: str,
    description: str | None,
    profile: BuyerProfile,
) -> tuple[int, PriceRead, str]:
    band = _band_for_category(category_key, profile)
    normal = band.normal_good_under
    special = band.special_good_under
    stretch = band.stretch_under

    if all_in is None:
        return 3, PriceRead.BAD, "Price read: unparsed price; assuming bad deal clarity."

    # Plain cashmere must be cheap unless design steps up
    if _is_plain_cashmere(title, description) and design in (DesignLevel.GENERIC, DesignLevel.WEAK, DesignLevel.POOR):
        if all_in <= normal:
            return 8, PriceRead.GOOD, "Plain knit; priced within normal band."
        if all_in <= special:
            return 4, PriceRead.FAIR, "Plain cashmere asking special-tier pricing without design merit."
        return 1, PriceRead.BAD, "Plain cashmere priced too high for generic design."

    # Allowed ceiling depends on design/make story
    allowed = normal
    price_read = PriceRead.GOOD

    if design is DesignLevel.AMAZING and make.value in ("good", "high", "exceptional"):
        allowed = stretch
        price_read = PriceRead.STRETCH if all_in > special else PriceRead.GOOD
    elif design is DesignLevel.GREAT and make.value in ("ordinary", "good", "high", "exceptional"):
        allowed = special + (stretch - special) * 0.33
        price_read = PriceRead.FAIR if all_in > special else PriceRead.GOOD
    elif design is DesignLevel.SIMPLE_TASTEFUL and make.value in ("high", "exceptional"):
        allowed = special
        price_read = PriceRead.FAIR if all_in > normal else PriceRead.GOOD
    else:
        allowed = normal
        price_read = PriceRead.GOOD if all_in <= normal else PriceRead.FAIR

    if all_in <= normal:
        pts = 10
        price_read = PriceRead.EXCELLENT if all_in <= normal * 0.65 else PriceRead.GOOD
        return pts, price_read, f"Price read: strong vs normal threshold ({normal:.0f})."

    if all_in <= special:
        pts = 7 if allowed >= special else 4
        return pts, price_read, f"Price read: within special band ({special:.0f}) for category."

    if all_in <= stretch and allowed >= stretch - 1:
        pts = 5
        return pts, PriceRead.STRETCH, f"Price read: stretch territory ({stretch:.0f}); needs love for item story."

    if all_in <= stretch:
        pts = 4
        return pts, PriceRead.STRETCH, "Price read: pricey versus allowed story; borderline."

    return 1, PriceRead.BAD, "Price read: above stretch without enough design/make justification."
