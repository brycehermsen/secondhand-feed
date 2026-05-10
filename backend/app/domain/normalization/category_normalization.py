from __future__ import annotations

from dataclasses import dataclass

from app.domain.models.buyer_profile import BuyerProfile


@dataclass(frozen=True)
class CategoryNormalization:
    category_key: str
    priority: str
    confidence: float
    read: str


def _contains_any(text: str, phrases: list[str]) -> str | None:
    t = text.lower()
    for p in phrases:
        if p.lower() in t:
            return p
    return None


def normalize_category(title: str, raw_category: str | None, profile: BuyerProfile) -> CategoryNormalization:
    blob = f"{title} {raw_category or ''}".lower()

    high = profile.categories.get("high_priority", [])
    med = profile.categories.get("medium_priority", [])
    low = profile.categories.get("low_priority", [])

    if hit := _contains_any(blob, high):
        return CategoryNormalization(hit, "high", 0.75, "High-priority category match.")
    if hit := _contains_any(blob, med):
        return CategoryNormalization(hit, "medium", 0.65, "Medium-priority category match.")
    if hit := _contains_any(blob, low):
        return CategoryNormalization(hit, "low", 0.55, "Low-priority category match.")

    # Fallback coarse buckets from title keywords
    outer = ["coat", "jacket", "parka", "blazer"]
    knit = ["knit", "sweater", "cardigan", "pullover"]
    shirt = ["shirt", "oxford", "button-down", "poplin"]
    pant = ["trouser", "pant", "denim", "jean"]
    shoe = ["boot", "loafer", "sneaker", "shoe"]

    if any(k in blob for k in knit):
        return CategoryNormalization("knitwear", "high", 0.45, "Inferred knitwear from title.")
    if any(k in blob for k in outer):
        return CategoryNormalization("outerwear", "high", 0.45, "Inferred outerwear from title.")
    if any(k in blob for k in shirt):
        return CategoryNormalization("shirts", "medium", 0.45, "Inferred shirts from title.")
    if any(k in blob for k in pant):
        return CategoryNormalization("trousers", "medium", 0.45, "Inferred trousers from title.")
    if any(k in blob for k in shoe):
        return CategoryNormalization("shoes", "medium", 0.45, "Inferred shoes from title.")

    return CategoryNormalization("unknown", "low", 0.2, "Category unclear.")
