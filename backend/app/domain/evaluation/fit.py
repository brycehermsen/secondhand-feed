from __future__ import annotations

from app.domain.models.enums import FitRead
from app.domain.normalization import SizeNormalization


def score_fit(
    size_norm: SizeNormalization,
    measurements: dict[str, str] | None,
    category_key: str,
) -> tuple[int, FitRead, str]:
    cat = category_key.lower()
    risky = any(k in cat for k in ("jacket", "coat", "blazer", "trouser", "pant", "shirt"))

    if size_norm.compatible:
        pts = 5
        read = "Fit read: size matches profile buckets."
        fit_read = FitRead.GOOD
        if risky and not measurements:
            pts = max(3, pts - 2)
            read += " Missing measurements on a tailored-ish category; reviewing is riskier."
            fit_read = FitRead.UNCERTAIN
        return pts, fit_read, read

    # Incompatible sizes should mostly be hard-filtered for tailored categories.
    if any(k in cat for k in ("knit", "sweater", "cardigan")):
        pts = 2
        return pts, FitRead.UNCERTAIN, "Fit read: size mismatch but knitwear can be forgiving; still risky."

    pts = 1
    return pts, FitRead.BAD, "Fit read: size looks wrong for preferences."
