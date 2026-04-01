"""Configuration — all secrets from env vars (Key Vault-backed in production)."""

import os


class Config:
    META_PIXEL_ID: str = os.environ.get("META_PIXEL_ID", "")
    META_ACCESS_TOKEN: str = os.environ.get("META_ACCESS_TOKEN", "")
    META_APP_SECRET: str = os.environ.get("META_APP_SECRET", "")
    META_APP_ID: str = os.environ.get("META_APP_ID", "971674085514908")
    META_API_VERSION: str = os.environ.get("META_API_VERSION", "v21.0")
    META_TEST_EVENT_CODE: str = os.environ.get("META_TEST_EVENT_CODE", "")
    DEAD_LETTER_QUEUE: str = os.environ.get("DEAD_LETTER_QUEUE", "meta-capi-deadletter")

    @property
    def capi_url(self) -> str:
        return f"https://graph.facebook.com/{self.META_API_VERSION}/{self.META_PIXEL_ID}/events"

    def validate(self) -> list[str]:
        errors = []
        if not self.META_PIXEL_ID:
            errors.append("META_PIXEL_ID not set")
        if not self.META_ACCESS_TOKEN:
            errors.append("META_ACCESS_TOKEN not set")
        return errors


config = Config()
