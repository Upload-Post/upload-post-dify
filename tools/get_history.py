from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from upload_post_api.dify_helpers import clean, client_from_credentials

FILTERS = ("platform", "status", "profile_username", "request_id", "job_id", "start", "end")


class GetHistoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = client_from_credentials(self.runtime.credentials)
        filters = {k: clean(tool_parameters.get(k)) for k in FILTERS}
        result = client.get_history(
            page=int(tool_parameters.get("page") or 1),
            limit=int(tool_parameters.get("limit") or 10),
            **{k: v for k, v in filters.items() if v is not None},
        )
        yield self.create_json_message(result)
