"""Session management - Maps Teams conversations to Amplifier sessions."""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from .config import settings
from .models import SessionMapping


class SessionManager:
    """Manages mapping between Teams conversations and Amplifier sessions."""

    def __init__(self):
        """Initialize session manager with in-memory storage."""
        self._sessions: dict[str, SessionMapping] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())

    async def stop(self):
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    def get_session(self, conversation_id: str) -> Optional[SessionMapping]:
        """Get session mapping for a Teams conversation."""
        return self._sessions.get(conversation_id)

    def create_session(
        self, conversation_id: str, amplifier_session_id: str, user_id: str
    ) -> SessionMapping:
        """Create a new session mapping."""
        mapping = SessionMapping(
            conversation_id=conversation_id,
            amplifier_session_id=amplifier_session_id,
            user_id=user_id,
        )
        self._sessions[conversation_id] = mapping
        return mapping

    def update_activity(self, conversation_id: str):
        """Update last activity timestamp for a session."""
        if conversation_id in self._sessions:
            self._sessions[conversation_id].last_activity = datetime.utcnow()
            self._sessions[conversation_id].message_count += 1

    def delete_session(self, conversation_id: str) -> bool:
        """Delete a session mapping."""
        if conversation_id in self._sessions:
            del self._sessions[conversation_id]
            return True
        return False

    def get_user_sessions(self, user_id: str) -> list[SessionMapping]:
        """Get all active sessions for a user."""
        return [s for s in self._sessions.values() if s.user_id == user_id]

    def get_session_count(self) -> int:
        """Get total number of active sessions."""
        return len(self._sessions)

    async def _cleanup_expired_sessions(self):
        """Background task to clean up expired sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                now = datetime.utcnow()
                timeout = timedelta(minutes=settings.session_timeout_minutes)

                expired = [
                    conv_id
                    for conv_id, mapping in self._sessions.items()
                    if now - mapping.last_activity > timeout
                ]

                for conv_id in expired:
                    del self._sessions[conv_id]

                if expired:
                    print(f"Cleaned up {len(expired)} expired sessions")

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in session cleanup: {e}")


# Global session manager instance
session_manager = SessionManager()
