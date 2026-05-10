from __future__ import annotations

import httpx

from app.domain.models.listing import RawListingSummary
from app.domain.models.source import SourceConfig
from app.ports.source_connector import SourceConnector


class EbayBrowseConnector(SourceConnector):
    """Public eBay search via Browse API (OAuth client credentials)."""

    source_type = "ebay_browse"

    def __init__(self, *, client_id: str | None, client_secret: str | None, marketplace_id: str):
        self.client_id = (client_id or "").strip() or None
        self.client_secret = (client_secret or "").strip() or None
        self.marketplace_id = marketplace_id or "EBAY_US"

    def fetch(self, config: SourceConfig) -> list[RawListingSummary]:
        if not self.client_id or not self.client_secret:
            raise RuntimeError("eBay credentials missing; set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET.")

        ephem = config.ephemeral or {}
        query = str(ephem.get("query", "")).strip()
        limit = int(ephem.get("limit", 20))
        limit = max(1, min(limit, 50))
        if not query:
            raise ValueError("eBay query required (pass ephemeral.query).")

        token = self._oauth_token()
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        params = {"q": query, "limit": str(limit)}
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": self.marketplace_id,
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            payload = resp.json()

        items = payload.get("itemSummaries") or []
        out: list[RawListingSummary] = []
        for item in items:
            item_id = item.get("itemId")
            web_url = item.get("itemWebUrl") or (f"https://www.ebay.com/itm/{item_id}" if item_id else None)
            if not web_url:
                continue
            title = str(item.get("title") or "Untitled listing")
            price = item.get("price") or {}
            value = price.get("value")
            currency = price.get("currency") or "USD"
            price_text = None
            if value is not None:
                price_text = f"{currency} {value}"

            shipping = item.get("shippingOptions") or []
            shipping_text = None
            if shipping:
                cost = (shipping[0] or {}).get("shippingCost") or {}
                if cost.get("value") is not None:
                    shipping_text = f"{cost.get('currency') or currency} {cost['value']} shipping"

            image_url = None
            img = item.get("image")
            if isinstance(img, dict):
                image_url = img.get("imageUrl")

            cond = item.get("condition")
            condition_text = None
            if isinstance(cond, str):
                condition_text = cond
            elif isinstance(cond, dict):
                condition_text = cond.get("conditionDisplayName") or cond.get("conditionId")

            brand_guess = None
            ep = item.get("additionalProductIdentifiers") or []
            if isinstance(ep, list) and ep:
                brand_guess = (ep[0] or {}).get("productIdentity")  # best-effort

            out.append(
                RawListingSummary(
                    marketplace="ebay",
                    canonical_url=str(web_url),
                    title=title,
                    brand_text=brand_guess,
                    price_text=price_text,
                    shipping_text=shipping_text,
                    image_url=image_url,
                    condition_text=condition_text,
                    size_text=None,
                    category_hint=None,
                    description=None,
                    seller_name=(item.get("seller") or {}).get("username") if isinstance(item.get("seller"), dict) else None,
                    design_level_hint=None,
                    make_quality_level_hint=None,
                    material_level_hint=None,
                    measurements=None,
                )
            )

        return out

    def _oauth_token(self) -> str:
        token_url = "https://api.ebay.com/identity/v1/oauth2/token"
        auth = (self.client_id, self.client_secret)
        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(token_url, data=data, headers=headers, auth=auth)
            resp.raise_for_status()
            payload = resp.json()
        token = payload.get("access_token")
        if not token:
            raise RuntimeError("eBay OAuth response missing access_token.")
        return str(token)
