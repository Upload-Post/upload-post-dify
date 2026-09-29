from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from upload_post_api import split_list
from upload_post_api.dify_helpers import clean, client_from_credentials


class GetAnalyticsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = client_from_credentials(self.runtime.credentials)
        days = tool_parameters.get("days")
        result = client.get_analytics(
            clean(tool_parameters.get("profile_username")),
            split_list(tool_parameters.get("platforms")),
            page_id=clean(tool_parameters.get("page_id")),
            page_urn=clean(tool_parameters.get("page_urn")),
            days=int(days) if days not in (None, "") else None,
        )
        yield self.create_json_message(result)
