# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "InovaComercioMS"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 5000

    SECRET_KEY: str = "change-me"
    JWT_SECRET_KEY: str = "change-me-too"
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600

    DATABASE_URL: str = "sqlite:///inovacomercio.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()