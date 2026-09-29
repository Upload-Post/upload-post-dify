from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from upload_post_api.dify_helpers import clean, client_from_credentials


class GetStatusTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = client_from_credentials(self.runtime.credentials)
        result = client.get_status(
            request_id=clean(tool_parameters.get("request_id")),
            job_id=clean(tool_parameters.get("job_id")),
        )
        yield self.create_json_message(result)
