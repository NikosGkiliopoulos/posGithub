# src/config.py

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite+aiosqlite:///./pos.db"


def get_settings() -> Settings:
    return Settings()
