from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from upload_post_api import split_list
from upload_post_api.dify_helpers import clean, client_from_credentials, publish_options


class UploadTextTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = client_from_credentials(self.runtime.credentials)
        result = client.upload_text(
            clean(tool_parameters.get("user")),
            split_list(tool_parameters.get("platforms")),
            clean(tool_parameters.get("text")),
            link_url=clean(tool_parameters.get("link_url")),
            **publish_options(tool_parameters),
        )
        yield self.create_json_message(result)
