from __future__ import annotations

from dataclasses import dataclass

from app.domain.models.buyer_profile import BuyerProfile
from app.domain.models.enums import BrandStatus


@dataclass(frozen=True)
class BrandNormalization:
    normalized_brand: str
    status: BrandStatus
    confidence: float
    read: str


def _norm(s: str | None) -> str:
    return (s or "").strip()


def normalize_brand(raw_brand: str | None, title: str, profile: BuyerProfile) -> BrandNormalization:
    """Pure brand normalization using profile lists only."""
    brand = _norm(raw_brand)
    blob = f"{brand} {title}".lower()

    target = {_norm(b).lower() for b in profile.brands.get("target", [])}
    credible = {_norm(b).lower() for b in profile.brands.get("credible_non_target", [])}
    watch = {_norm(b).lower() for b in profile.brands.get("reputation_watchlist", [])}
    excluded = {_norm(b).lower() for b in profile.brands.get("excluded", [])}

    def matches(seed: set[str]) -> str | None:
        for name in seed:
            if not name:
                continue
            if brand.lower() == name or name in blob:
                return name.title() if brand.lower() != name else brand
        return None

    ex = matches(excluded)
    if ex:
        return BrandNormalization(ex, BrandStatus.EXCLUDED, 0.85, "Excluded brand / line matched.")

    tg = matches(target)
    if tg:
        return BrandNormalization(tg, BrandStatus.TARGET, 0.9, "Target brand.")

    cd = matches(credible)
    if cd:
        return BrandNormalization(cd, BrandStatus.CREDIBLE_NON_TARGET, 0.75, "Credible non-target brand.")

    wt = matches(watch)
    if wt:
        return BrandNormalization(wt, BrandStatus.REPUTATION_WATCHLIST, 0.55, "Watchlist brand; no automatic boost.")

    if brand:
        return BrandNormalization(brand, BrandStatus.UNKNOWN, 0.35, "Unknown brand; must earn the feed.")

    return BrandNormalization("Unknown", BrandStatus.UNKNOWN, 0.2, "Brand missing; low confidence.")
