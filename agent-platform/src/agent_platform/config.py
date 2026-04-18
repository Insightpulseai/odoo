"""Thin config helpers — env-aware feature flags."""

from __future__ import annotations

from agent_platform.settings import Settings, get_settings


def is_production(settings: Settings | None = None) -> bool:
    s = settings or get_settings()
    return s.env == "production"


def is_development(settings: Settings | None = None) -> bool:
    s = settings or get_settings()
    return s.env == "development"
