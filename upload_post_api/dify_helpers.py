"""Helpers shared by the Dify tool classes."""

from __future__ import annotations

from typing import Any

from upload_post_api.client import UploadPostClient


def client_from_credentials(credentials: dict[str, Any]) -> UploadPostClient:
    return UploadPostClient(credentials.get("api_key", ""))


def clean(value: Any) -> Any:
    """Normalise empty strings from Dify forms to ``None``."""
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def publish_options(params: dict[str, Any]) -> dict[str, Any]:
    """Options shared by the three publishing tools."""
    return {
        "scheduled_date": clean(params.get("scheduled_date")),
        "timezone": clean(params.get("timezone")),
        "add_to_queue": params.get("add_to_queue") or None,
        "first_comment": clean(params.get("first_comment")),
    }
