from __future__ import annotations

from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    id: str
    name: str
    source_type: str
    marketplace: str
    enabled: bool = True
    ephemeral: dict[str, object] | None = Field(
        default=None,
        description="Request-local connector inputs; not persisted.",
    )


class SourceRun(BaseModel):
    id: str
    source_id: str
    status: str
    started_at: str | None = None
    finished_at: str | None = None
    listings_found: int = 0
    listings_new: int = 0
    listings_updated: int = 0
    error_message: str | None = None
    logs_json: str | None = Field(default=None)
