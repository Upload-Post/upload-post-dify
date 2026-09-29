from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from upload_post_api.dify_helpers import client_from_credentials


class ListProfilesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = client_from_credentials(self.runtime.credentials)
        yield self.create_json_message(client.list_profiles())
