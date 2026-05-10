from __future__ import annotations

from app.domain.models.enums import BrandStatus
from app.domain.normalization import BrandNormalization


def score_brand(brand: BrandNormalization) -> tuple[int, str]:
    """Returns brand points 0-8 and rationale."""
    match brand.status:
        case BrandStatus.TARGET:
            return 8, "Core target brand."
        case BrandStatus.CREDIBLE_NON_TARGET:
            return 6, "Credible non-target; needs strong item signals."
        case BrandStatus.REPUTATION_WATCHLIST:
            return 3, "Watchlist brand; earns credibility via item quality only."
        case BrandStatus.EXCLUDED:
            return 0, "Excluded brand."
        case BrandStatus.UNKNOWN:
            return 2, "Unknown brand; needs exceptional item + price to surface."
    return 0, "Brand neutral."
