"""
Configuration - reads from environment variables / .env file
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
        # Multi-account: JUNIOR_ACCOUNTS='[{"email":"a@b.com","password":"x","tenant_id":"tm_xx"}]'
        raw = os.getenv("JUNIOR_ACCOUNTS", "")
        if raw:
            return json.loads(raw)

        # Single account fallback
        email = os.getenv("JUNIOR_EMAIL", "")
        password = os.getenv("JUNIOR_PASSWORD", "")
        if email and password:
            return [{"email": email, "password": password, "tenant_id": self.default_tenant_id}]

        return []


settings = Settings()
