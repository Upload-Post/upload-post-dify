"""Minimal HTTP client for the Upload-Post REST API.

Only documented endpoints and parameters are used, see
https://docs.upload-post.com/api/reference
"""

from __future__ import annotations

from typing import Any

import requests

BASE_URL = "https://api.upload-post.com/api"
DEFAULT_TIMEOUT = 60
USER_AGENT = "upload-post-dify-plugin/0.1.0"


class UploadPostAPIError(Exception):
    """Raised when the Upload-Post API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def split_list(value: Any) -> list[str]:
    """Turn ``"a, b\\nc"`` or ``["a", "b"]`` into ``["a", "b", "c"]``."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        items = [str(v) for v in value]
    else:
        items = str(value).replace("\n", ",").split(",")
    return [item.strip() for item in items if item and item.strip()]


def _is_http_url(value: str) -> bool:
    return value.lower().startswith(("http://", "https://"))


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return bool(value)


class UploadPostClient:
    """Thin wrapper around the endpoints used by the Dify tools."""

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        if not api_key or not str(api_key).strip():
            raise UploadPostAPIError("Upload-Post API key is missing.")
        self._api_key = str(api_key).strip()
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or requests.Session()

    # ----------------------------------------------------------------- core
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: list[tuple[str, str]] | None = None,
    ) -> dict[str, Any]:
        headers = {
            "Authorization": f"Apikey {self._api_key}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }
        try:
            response = self._session.request(
                method,
                f"{self._base_url}{path}",
                headers=headers,
                params={k: v for k, v in (params or {}).items() if v not in (None, "")},
                data=data,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            # Never include the request (and its headers) in the message.
            raise UploadPostAPIError(
                f"Could not reach the Upload-Post API: {type(exc).__name__}"
            ) from None

        try:
            payload = response.json()
        except ValueError:
            payload = None

        if response.status_code >= 400:
            message = None
            if isinstance(payload, dict):
                message = payload.get("message") or payload.get("error")
            if not message:
                message = (response.text or "").strip()[:300] or response.reason
            raise UploadPostAPIError(
                f"Upload-Post API error {response.status_code}: {message}",
                status_code=response.status_code,
            )
        if payload is None:
            raise UploadPostAPIError("Upload-Post API returned a non-JSON response.")
        if not isinstance(payload, dict):
            payload = {"result": payload}
        return payload

    @staticmethod
    def _publish_form(
        user: str,
        platforms: list[str],
        *,
        title: str | None = None,
        description: str | None = None,
        scheduled_date: str | None = None,
        timezone: str | None = None,
        add_to_queue: Any = None,
        first_comment: str | None = None,
        async_upload: Any = None,
    ) -> list[tuple[str, str]]:
        if not user:
            raise UploadPostAPIError("A profile (user) is required.")
        if not platforms:
            raise UploadPostAPIError("At least one platform is required.")
        if scheduled_date and _truthy(add_to_queue):
            raise UploadPostAPIError(
                "scheduled_date and add_to_queue cannot be used together."
            )
        form: list[tuple[str, str]] = [("user", user)]
        form += [("platform[]", p) for p in platforms]
        optional = {
            "title": title,
            "description": description,
            "scheduled_date": scheduled_date,
            "timezone": timezone,
            "first_comment": first_comment,
        }
        form += [(k, str(v)) for k, v in optional.items() if v not in (None, "")]
        if add_to_queue is not None and _truthy(add_to_queue):
            form.append(("add_to_queue", "true"))
        if async_upload is not None:
            form.append(("async_upload", "true" if _truthy(async_upload) else "false"))
        return form

    # ------------------------------------------------------------ endpoints
    def me(self) -> dict[str, Any]:
        """``GET /api/uploadposts/me`` - validates the API key."""
        return self._request("GET", "/uploadposts/me")

    def upload_text(
        self,
        user: str,
        platforms: list[str],
        text: str,
        *,
        link_url: str | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """``POST /api/upload_text``."""
        if not text:
            raise UploadPostAPIError("The post text is required.")
        form = self._publish_form(user, platforms, title=text, **options)
        if link_url:
            form.append(("link_url", link_url))
        return self._request("POST", "/upload_text", data=form)

    def upload_video(
        self, user: str, platforms: list[str], video_url: str, **options: Any
    ) -> dict[str, Any]:
        """``POST /api/upload`` with a public video URL."""
        if not video_url or not _is_http_url(video_url):
            raise UploadPostAPIError("video_url must be a public http(s) URL.")
        form = self._publish_form(user, platforms, **options)
        form.append(("video", video_url))
        return self._request("POST", "/upload", data=form)

    def upload_photos(
        self, user: str, platforms: list[str], photo_urls: list[str], **options: Any
    ) -> dict[str, Any]:
        """``POST /api/upload_photos`` with public image URLs."""
        if not photo_urls:
            raise UploadPostAPIError("At least one photo URL is required.")
        bad = [u for u in photo_urls if not _is_http_url(u)]
        if bad:
            raise UploadPostAPIError("photo_urls must be public http(s) URLs.")
        form = self._publish_form(user, platforms, **options)
        form += [("photos[]", url) for url in photo_urls]
        return self._request("POST", "/upload_photos", data=form)

    def get_status(
        self, request_id: str | None = None, job_id: str | None = None
    ) -> dict[str, Any]:
        """``GET /api/uploadposts/status`` by ``request_id`` or ``job_id``."""
        if not request_id and not job_id:
            raise UploadPostAPIError("Provide either request_id or job_id.")
        params = {"request_id": request_id} if request_id else {"job_id": job_id}
        return self._request("GET", "/uploadposts/status", params=params)

    def list_profiles(self) -> dict[str, Any]:
        """``GET /api/uploadposts/users``."""
        return self._request("GET", "/uploadposts/users")

    def get_history(
        self,
        page: int = 1,
        limit: int = 10,
        **filters: Any,
    ) -> dict[str, Any]:
        """``GET /api/uploadposts/history`` with the documented filters."""
        allowed = {
            "platform",
            "status",
            "profile_username",
            "request_id",
            "job_id",
            "start",
            "end",
        }
        unknown = set(filters) - allowed
        if unknown:
            raise UploadPostAPIError(f"Unknown history filters: {sorted(unknown)}")
        if bool(filters.get("start")) != bool(filters.get("end")):
            raise UploadPostAPIError("start and end must be used together.")
        if limit not in (10, 20, 50, 100):
            raise UploadPostAPIError("limit must be one of 10, 20, 50 or 100.")
        params: dict[str, Any] = {"page": max(int(page), 1), "limit": limit}
        params.update(filters)
        return self._request("GET", "/uploadposts/history", params=params)

    def get_analytics(
        self,
        profile_username: str,
        platforms: list[str],
        *,
        page_id: str | None = None,
        page_urn: str | None = None,
        days: int | None = None,
    ) -> dict[str, Any]:
        """``GET /api/analytics/{profile_username}``."""
        if not profile_username:
            raise UploadPostAPIError("profile_username is required.")
        if not platforms:
            raise UploadPostAPIError("At least one platform is required.")
        params: dict[str, Any] = {
            "platforms": ",".join(platforms),
            "page_id": page_id,
            "page_urn": page_urn,
            "days": days,
        }
        path = f"/analytics/{requests.utils.quote(profile_username, safe='')}"
        return self._request("GET", path, params=params)
