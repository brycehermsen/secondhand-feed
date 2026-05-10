from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.models import BuyerProfile, RawListingSummary, SourceConfig


@runtime_checkable
class ProfileStore(Protocol):
    def load(self) -> BuyerProfile: ...

    def save(self, profile: BuyerProfile) -> None: ...


@runtime_checkable
class SourceConnector(Protocol):
    source_type: str

    def fetch(self, config: SourceConfig) -> list[RawListingSummary]: ...
