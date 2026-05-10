from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.models.buyer_profile import BuyerProfile


@dataclass(frozen=True)
class SizeNormalization:
    normalized_tokens: list[str]
    compatible: bool
    confidence: float
    read: str


_TOKEN_RE = re.compile(r"[a-z0-9./]+", re.I)


def _tokens(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [m.group(0).upper() for m in _TOKEN_RE.finditer(raw)]


def _flatten_sizes(profile: BuyerProfile) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for bucket, cfg in profile.sizes.items():
        likely = cfg.get("likely_sizes", [])
        out[bucket] = [str(s).strip().upper() for s in likely]
    return out


def normalize_size(
    raw_size: str | None,
    title: str,
    category: str,
    profile: BuyerProfile,
) -> SizeNormalization:
    tokens = _tokens(raw_size) + _tokens(title)
    sizes_map = _flatten_sizes(profile)

    cat_l = category.lower()
    bucket_keys: list[str] = []
    if any(k in cat_l for k in ("knit", "sweater", "shirt", "top", "overshirt")):
        bucket_keys.extend(["tops", "shirts"])
    if any(k in cat_l for k in ("coat", "jacket", "outer", "chore")):
        bucket_keys.extend(["jackets"])
    if any(k in cat_l for k in ("trouser", "pant", "denim")):
        bucket_keys.extend(["pants"])
    if "shoe" in cat_l or "boot" in cat_l or "loafer" in cat_l:
        bucket_keys.extend(["shoes"])

    # Default to tops/jackets if unknown — slightly conservative
    if not bucket_keys:
        bucket_keys = ["tops", "jackets"]

    acceptable: set[str] = set()
    for bk in bucket_keys:
        acceptable.update(sizes_map.get(bk, []))

    if not acceptable:
        return SizeNormalization(tokens, True, 0.25, "No size preferences configured for this category.")

    matched = [t for t in tokens if t in acceptable]
    if matched:
        return SizeNormalization(matched, True, 0.75, "Size aligns with likely sizes.")

    if not tokens:
        return SizeNormalization([], False, 0.35, "Size missing; risky for tailored categories.")

    return SizeNormalization(tokens, False, 0.65, "Size likely outside preferred range.")
