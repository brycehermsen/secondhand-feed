from __future__ import annotations

from pydantic import BaseModel


class FeedbackEvent(BaseModel):
    id: str
    listing_id: str
    action: str
    reason: str | None = None
    notes: str | None = None
    created_at: str
