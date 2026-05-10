from __future__ import annotations

from pathlib import Path

import yaml

from app.domain.models.buyer_profile import BuyerProfile
from app.ports.source_connector import ProfileStore


class YamlProfileStore(ProfileStore):
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> BuyerProfile:
        raw_text = self.path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw_text)
        if not isinstance(data, dict):
            raise ValueError("YAML root must be a mapping")
        return BuyerProfile.model_validate(data)

    def save(self, profile: BuyerProfile) -> None:
        dumped = profile.model_dump(mode="python")
        text = yaml.safe_dump(dumped, sort_keys=False, allow_unicode=True)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(text, encoding="utf-8")
