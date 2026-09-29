from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from upload_post_api import split_list
from upload_post_api.dify_helpers import clean, client_from_credentials, publish_options


class UploadVideoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = client_from_credentials(self.runtime.credentials)
        result = client.upload_video(
            clean(tool_parameters.get("user")),
            split_list(tool_parameters.get("platforms")),
            clean(tool_parameters.get("video_url")),
            title=clean(tool_parameters.get("title")),
            description=clean(tool_parameters.get("description")),
            # Video processing can take minutes: return a request_id right away
            # and let the user poll it with the Get Upload Status tool.
            async_upload=True,
            **publish_options(tool_parameters),
        )
        yield self.create_json_message(result)
