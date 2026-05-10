from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PriceNormalization:
    item_price: float | None
    shipping: float | None
    all_in: float | None
    currency: str
    confidence: float
    read: str


_MONEY_RE = re.compile(r"[$€£]?\s*([0-9]+(?:[.,][0-9]+)?)")


def _first_money(text: str | None) -> float | None:
    if not text:
        return None
    m = _MONEY_RE.search(text.replace(",", ""))
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def normalize_price(price_text: str | None, shipping_text: str | None) -> PriceNormalization:
    item = _first_money(price_text)
    ship = _first_money(shipping_text)
    all_in = None
    if item is not None:
        all_in = item + (ship or 0.0)

    if item is None:
        return PriceNormalization(None, ship, None, "USD", 0.2, "Could not parse item price.")

    read = f"Parsed item {item:.0f}" + (f", shipping {ship:.0f}" if ship is not None else "")
    return PriceNormalization(item, ship, all_in, "USD", 0.7, read + ".")
