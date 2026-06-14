"""
Authentication and session management for Junior.so
Handles login, token refresh, and multi-account rotation.
"""

import asyncio
import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)


class JuniorSession:
    def __init__(self, email: str, password: str, tenant_id: str):
        self.email = email
        self.password = password
        self.tenant_id = tenant_id
        self.token: Optional[str] = None
        self.uid: Optional[str] = None
        self.conversation_id: Optional[str] = None
        self._lock = asyncio.Lock()

    @property
    def headers(self) -> dict:
        return {
            "accept": "*/*",
            "accept-language": "en",
            "junior-id": self.tenant_id,
            "token": self.token or "",
            "uid": self.uid or "",
            "origin": "https://junior.so",
            "referer": f"https://junior.so/c?junior={self.tenant_id}",
            "user-agent": "junior2api/0.1 (+https://github.com/venjye/junior2api)",
        }

    async def login(self, client: httpx.AsyncClient) -> None:
        """Login and store credentials."""
        resp = await client.post(
            f"{settings.base_url}/api/auth/login",
            json={"email": self.email, "password": self.password},
            timeout=15,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Login failed ({resp.status_code}): {resp.text}")

        data = resp.json()
        self.token = data.get("token") or data.get("access_token")
        self.uid = data.get("uid") or data.get("user_id") or data.get("id")

        if not self.token:
            raise RuntimeError("Login response has no token")

        logger.info(f"Logged in as {self.email} (uid={self.uid})")

    async def ensure_conversation(self, client: httpx.AsyncClient) -> str:
        """Get or create a conversation."""
        if not self.conversation_id:
            resp = await client.post(
                f"{settings.base_url}/api/c/conversations",
                headers=self.headers,
                json={},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            self.conversation_id = data.get("id") or data.get("conversation_id")
            logger.info(f"Created conversation {self.conversation_id}")
        return self.conversation_id

    def is_auth_error(self, status: int, body: dict) -> bool:
        if status in (401, 403):
            return True
        msg = str(body.get("message", "") or body.get("error", "")).lower()
        return "unauthorized" in msg or "expired" in msg or "invalid token" in msg


class SessionManager:
    """
    Manages one or more Junior.so sessions.
    Supports multi-account round-robin rotation.
    """

    def __init__(self):
        self._sessions: list[JuniorSession] = []
        self._current = 0
        self._client: Optional[httpx.AsyncClient] = None

    async def init(self):
        self._client = httpx.AsyncClient()

        accounts = settings.accounts
        if not accounts:
            raise RuntimeError(
                "No accounts configured. Set JUNIOR_EMAIL/JUNIOR_PASSWORD "
                "or JUNIOR_ACCOUNTS in .env"
            )

        for acc in accounts:
            session = JuniorSession(
                email=acc["email"],
                password=acc["password"],
                tenant_id=acc.get("tenant_id", settings.default_tenant_id),
            )
            await session.login(self._client)
            self._sessions.append(session)

        logger.info(f"Initialized {len(self._sessions)} session(s)")

    def _next_session(self) -> JuniorSession:
        session = self._sessions[self._current % len(self._sessions)]
        self._current += 1
        return session

    async def send_message(self, text: str, max_retries: int = 1) -> str:
        session = self._next_session()

        async with session._lock:
            for attempt in range(max_retries + 1):
                try:
                    conv_id = await session.ensure_conversation(self._client)
                    resp = await self._client.post(
                        f"{settings.base_url}/api/c/conversations/{conv_id}/messages",
                        headers=session.headers,
                        files={"text": (None, text)},
                        timeout=60,
                    )

                    if session.is_auth_error(resp.status_code, {}):
                        if attempt < max_retries:
                            logger.info("Token expired, re-logging in...")
                            await session.login(self._client)
                            session.conversation_id = None
                            continue
                        raise RuntimeError("Authentication failed after retry")

                    resp.raise_for_status()
                    data = resp.json()

                    return (
                        data.get("reply")
                        or data.get("message")
                        or data.get("content")
                        or data.get("text")
                        or str(data)
                    )

                except httpx.TimeoutException:
                    raise RuntimeError("Request timed out")

        raise RuntimeError("Send failed")
