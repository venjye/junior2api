"""
Session management for Junior.so
Uses static token extracted from browser — no password required.
Junior.so uses magic-link (email code) login, so we work with a pre-extracted token.
"""

import asyncio
import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)


class JuniorSession:
    def __init__(self, token: str, uid: str, tenant_id: str):
        self.token = token
        self.uid = uid
        self.tenant_id = tenant_id
        self.conversation_id: Optional[str] = None
        self._lock = asyncio.Lock()

    @property
    def headers(self) -> dict:
        return {
            "accept": "*/*",
            "accept-language": "en",
            "junior-id": self.tenant_id,
            "token": self.token,
            "uid": self.uid,
            "origin": "https://junior.so",
            "referer": f"https://junior.so/c?junior={self.tenant_id}",
            "user-agent": "junior2api/0.1 (+https://github.com/venjye/junior2api)",
        }

    def is_auth_error(self, status: int) -> bool:
        return status in (401, 403)

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


class SessionManager:
    """
    Manages one or more Junior.so sessions with static tokens.
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
                "No accounts configured.\n"
                "Set JUNIOR_TOKEN + JUNIOR_UID + JUNIOR_TENANT_ID in .env\n"
                "See GET_TOKEN.md for how to get your token from browser DevTools."
            )

        for acc in accounts:
            session = JuniorSession(
                token=acc["token"],
                uid=acc["uid"],
                tenant_id=acc.get("tenant_id", settings.default_tenant_id),
            )
            self._sessions.append(session)

        logger.info(f"Loaded {len(self._sessions)} session(s)")

    def _next_session(self) -> JuniorSession:
        session = self._sessions[self._current % len(self._sessions)]
        self._current += 1
        return session

    async def send_message(self, text: str) -> str:
        session = self._next_session()

        async with session._lock:
            conv_id = await session.ensure_conversation(self._client)
            resp = await self._client.post(
                f"{settings.base_url}/api/c/conversations/{conv_id}/messages",
                headers=session.headers,
                files={"text": (None, text)},
                timeout=60,
            )

            if session.is_auth_error(resp.status_code):
                raise RuntimeError(
                    f"Token expired or invalid (HTTP {resp.status_code}).\n"
                    "Please refresh your token — see GET_TOKEN.md for instructions."
                )

            resp.raise_for_status()
            data = resp.json()

            return (
                data.get("reply")
                or data.get("message")
                or data.get("content")
                or data.get("text")
                or str(data)
            )
