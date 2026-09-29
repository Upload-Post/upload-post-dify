from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from upload_post_api import UploadPostAPIError, UploadPostClient


class UploadPostProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Validate the API key against ``GET /api/uploadposts/me``."""
        try:
            result = UploadPostClient(credentials.get("api_key", ""), timeout=20).me()
        except UploadPostAPIError as exc:
            if exc.status_code in (401, 403):
                raise ToolProviderCredentialValidationError(
                    "Invalid Upload-Post API key."
                ) from None
            raise ToolProviderCredentialValidationError(str(exc)) from None
        if not result.get("success", True):
            raise ToolProviderCredentialValidationError(
                result.get("message") or "Invalid Upload-Post API key."
            )
