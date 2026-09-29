"""Read-only smoke test against the real Upload-Post API.

Runs the Dify tool classes (List Profiles and Get Upload History) and the
provider credential check. Nothing is published.

    UPLOAD_POST_API_KEY=... python scripts/live_readonly_check.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from provider.upload_post import UploadPostProvider  # noqa: E402
from tools.get_history import GetHistoryTool  # noqa: E402
from tools.list_profiles import ListProfilesTool  # noqa: E402


def main() -> None:
    creds = {"api_key": os.environ["UPLOAD_POST_API_KEY"]}

    UploadPostProvider()._validate_credentials(creds)
    print("provider credential check (GET /uploadposts/me): OK")

    [msg] = list(ListProfilesTool.from_credentials(creds)._invoke({}))
    profiles = msg.message.json_object
    users = profiles.get("profiles") or profiles.get("users") or []
    print(f"list_profiles: OK, keys={sorted(profiles)}, profiles={len(users)}")

    [msg] = list(GetHistoryTool.from_credentials(creds)._invoke({"page": 1, "limit": 10}))
    history = msg.message.json_object
    rows = history.get("history") or []
    print(f"get_history: OK, keys={sorted(history)}, rows={len(rows)}")


if __name__ == "__main__":
    main()
