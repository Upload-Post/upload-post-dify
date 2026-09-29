"""Offline tests: the HTTP layer is mocked, no network access."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from upload_post_api import UploadPostAPIError, UploadPostClient, split_list

ROOT = Path(__file__).resolve().parent.parent


def _response(status: int = 200, payload: object | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = payload if payload is not None else {"success": True}
    resp.text = ""
    resp.reason = "reason"
    return resp


def _client(payload: object | None = None, status: int = 200):
    session = MagicMock()
    session.request.return_value = _response(status, payload)
    return UploadPostClient("secret-key", session=session), session


def test_split_list():
    assert split_list("tiktok, instagram\nx,,") == ["tiktok", "instagram", "x"]
    assert split_list(["a", " b "]) == ["a", "b"]
    assert split_list(None) == []


def test_auth_header_uses_apikey_scheme():
    client, session = _client()
    client.me()
    _, kwargs = session.request.call_args
    assert kwargs["headers"]["Authorization"] == "Apikey secret-key"
    assert session.request.call_args.args[:2] == (
        "GET",
        "https://api.upload-post.com/api/uploadposts/me",
    )


def test_upload_text_form():
    client, session = _client()
    client.upload_text(
        "acme", ["x", "linkedin"], "Hello", link_url="https://a.b", first_comment="hi"
    )
    method, url = session.request.call_args.args
    data = session.request.call_args.kwargs["data"]
    assert (method, url) == ("POST", "https://api.upload-post.com/api/upload_text")
    assert ("user", "acme") in data
    assert ("platform[]", "x") in data and ("platform[]", "linkedin") in data
    assert ("title", "Hello") in data
    assert ("link_url", "https://a.b") in data
    assert ("first_comment", "hi") in data


def test_upload_video_requires_url_and_sends_async():
    client, session = _client()
    with pytest.raises(UploadPostAPIError):
        client.upload_video("acme", ["tiktok"], "/etc/passwd")
    client.upload_video("acme", ["tiktok"], "https://x.y/v.mp4", async_upload=True)
    data = session.request.call_args.kwargs["data"]
    assert ("video", "https://x.y/v.mp4") in data
    assert ("async_upload", "true") in data


def test_upload_photos_multiple_urls():
    client, session = _client()
    client.upload_photos("acme", ["instagram"], ["https://a/1.jpg", "https://a/2.jpg"])
    data = session.request.call_args.kwargs["data"]
    assert [v for k, v in data if k == "photos[]"] == ["https://a/1.jpg", "https://a/2.jpg"]


def test_schedule_and_queue_are_exclusive():
    client, _ = _client()
    with pytest.raises(UploadPostAPIError):
        client.upload_text("acme", ["x"], "t", scheduled_date="2030-01-01T00:00:00Z", add_to_queue=True)


def test_status_needs_an_id():
    client, session = _client()
    with pytest.raises(UploadPostAPIError):
        client.get_status()
    client.get_status(job_id="j1")
    assert session.request.call_args.kwargs["params"] == {"job_id": "j1"}


def test_history_validation_and_params():
    client, session = _client()
    with pytest.raises(UploadPostAPIError):
        client.get_history(limit=7)
    with pytest.raises(UploadPostAPIError):
        client.get_history(start="2026-01-01")
    client.get_history(page=2, limit=20, status="failed")
    assert session.request.call_args.kwargs["params"] == {"page": 2, "limit": 20, "status": "failed"}


def test_analytics_params():
    client, session = _client()
    client.get_analytics("my profile", ["instagram", "x"], days=7)
    args, kwargs = session.request.call_args
    assert args[1].endswith("/analytics/my%20profile")
    assert kwargs["params"]["platforms"] == "instagram,x"
    assert kwargs["params"]["days"] == 7


def test_error_message_does_not_leak_key():
    client, _ = _client({"message": "Invalid API key"}, status=401)
    with pytest.raises(UploadPostAPIError) as exc:
        client.me()
    assert exc.value.status_code == 401
    assert "secret-key" not in str(exc.value)


# ----------------------------------------------------------------- Dify layer
def _run_tool(tool_cls, params, payload=None):
    tool = tool_cls.from_credentials({"api_key": "secret-key"})
    with patch("upload_post_api.client.requests.Session") as session_cls:
        session_cls.return_value.request.return_value = _response(200, payload or {"ok": 1})
        messages = list(tool._invoke(params))
        return messages, session_cls.return_value.request


def test_tool_upload_video_invocation():
    from tools.upload_video import UploadVideoTool

    messages, request = _run_tool(
        UploadVideoTool,
        {"user": "acme", "platforms": "tiktok, youtube", "video_url": "https://a/v.mp4",
         "title": "T", "description": "", "add_to_queue": False},
    )
    data = request.call_args.kwargs["data"]
    assert ("platform[]", "youtube") in data and ("title", "T") in data
    assert not any(k == "description" for k, _ in data)
    assert not any(k == "add_to_queue" for k, _ in data)
    assert messages[0].message.json_object == {"ok": 1}


def test_tool_history_invocation():
    from tools.get_history import GetHistoryTool

    _, request = _run_tool(GetHistoryTool, {"page": 1, "limit": "50", "platform": "", "status": "success"})
    assert request.call_args.kwargs["params"] == {"page": 1, "limit": 50, "status": "success"}


def test_provider_validation_rejects_bad_key():
    from dify_plugin.errors.tool import ToolProviderCredentialValidationError

    from provider.upload_post import UploadPostProvider

    with patch("upload_post_api.client.requests.Session") as session_cls:
        session_cls.return_value.request.return_value = _response(401, {"message": "bad"})
        with pytest.raises(ToolProviderCredentialValidationError):
            UploadPostProvider()._validate_credentials({"api_key": "nope"})


def test_every_tool_yaml_points_to_existing_source():
    provider = yaml.safe_load((ROOT / "provider/upload_post.yaml").read_text())
    names = []
    for rel in provider["tools"]:
        spec = yaml.safe_load((ROOT / rel).read_text())
        assert (ROOT / spec["extra"]["python"]["source"]).is_file()
        names.append(spec["identity"]["name"])
        for param in spec["parameters"]:
            assert "reddit" not in str(param).lower()
    assert names == [
        "upload_text", "upload_video", "upload_photos", "get_status",
        "list_profiles", "get_history", "get_analytics",
    ]
