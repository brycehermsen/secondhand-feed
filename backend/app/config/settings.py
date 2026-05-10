from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_path: str = Field(alias="DATABASE_PATH", default="../data/app.db")
    profile_path: str = Field(alias="PROFILE_PATH", default="../data/buyer_style_profile.yaml")
    fake_fixture_path: str = Field(alias="FAKE_FIXTURE_PATH", default="")
    ebay_client_id: str | None = Field(alias="EBAY_CLIENT_ID", default=None)
    ebay_client_secret: str | None = Field(alias="EBAY_CLIENT_SECRET", default=None)
    ebay_marketplace_id: str = Field(alias="EBAY_MARKETPLACE_ID", default="EBAY_US")

    def resolved_fixture_path(self) -> Path:
        if self.fake_fixture_path.strip():
            return Path(self.fake_fixture_path)
        here = Path(__file__).resolve().parents[1]
        return here / "app" / "adapters" / "sources" / "fixtures" / "fake_listings.json"


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

