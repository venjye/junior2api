"""
Configuration - reads from environment variables / .env file

Auth mode:
  Token mode (recommended):  set JUNIOR_TOKEN + JUNIOR_UID + JUNIOR_TENANT_ID
  Multi-account:              set JUNIOR_ACCOUNTS as JSON array
"""

import json
import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


class Settings:
    base_url: str = os.getenv("JUNIOR_BASE_URL", "https://junior.so")
    default_tenant_id: str = os.getenv("JUNIOR_TENANT_ID", "")
    api_key: str = os.getenv("API_KEY", "")  # optional: protect your endpoint

    @property
    def accounts(self) -> List[dict]:
        # Multi-account JSON array
        # JUNIOR_ACCOUNTS='[{"token":"xxx","uid":"u_xxx","tenant_id":"tm_xxx"}]'
        raw = os.getenv("JUNIOR_ACCOUNTS", "")
        if raw:
            return json.loads(raw)

        # Single account from token
        token = os.getenv("JUNIOR_TOKEN", "")
        uid = os.getenv("JUNIOR_UID", "")
        if token and uid:
            return [{"token": token, "uid": uid, "tenant_id": self.default_tenant_id}]

        return []


settings = Settings()
