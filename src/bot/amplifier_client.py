"""Client for interacting with the Amplifier API."""

import httpx

from .config import settings
from .models import AmplifierMessageRequest, AmplifierMessageResponse, AmplifierSessionRequest


class AmplifierClient:
    """HTTP client for Amplifier API operations."""

    def __init__(self):
        """Initialize the Amplifier client."""
        self.base_url = settings.amplifier_api_url.rstrip("/")
        self.api_key = settings.amplifier_api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def create_session(self, metadata: dict | None = None) -> str:
        """Create a new Amplifier session.

        Args:
            metadata: Optional metadata to attach to the session

        Returns:
            Session ID

        Raises:
            httpx.HTTPError: If the API request fails
        """
        request = AmplifierSessionRequest(
            base_config_id=settings.amplifier_base_config_id,
            base_config_name=settings.amplifier_base_config_name,
            metadata=metadata,
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sessions",
                headers=self.headers,
                json=request.model_dump(exclude_none=True),
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["session_id"]

    async def send_message(self, session_id: str, content: str) -> AmplifierMessageResponse:
        """Send a message to an Amplifier session.

        Args:
            session_id: The session ID
            content: Message content to send

        Returns:
            Response from Amplifier

        Raises:
            httpx.HTTPError: If the API request fails
        """
        request = AmplifierMessageRequest(content=content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sessions/{session_id}/messages",
                headers=self.headers,
                json=request.model_dump(),
                timeout=120.0,  # Longer timeout for LLM responses
            )
            response.raise_for_status()
            data = response.json()

            # Extract the assistant's response
            # API returns list of messages, we want the last assistant message
            messages = data.get("messages", [])
            assistant_messages = [m for m in messages if m.get("role") == "assistant"]

            if assistant_messages:
                last_message = assistant_messages[-1]
                return AmplifierMessageResponse(
                    role=last_message["role"],
                    content=last_message["content"],
                    timestamp=last_message.get("timestamp"),
                )
            else:
                # Fallback if no assistant message found
                return AmplifierMessageResponse(
                    role="assistant",
                    content="I received your message but couldn't generate a response.",
                )

    async def get_session_info(self, session_id: str) -> dict:
        """Get information about a session.

        Args:
            session_id: The session ID

        Returns:
            Session information

        Raises:
            httpx.HTTPError: If the API request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/sessions/{session_id}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def delete_session(self, session_id: str) -> bool:
        """Delete an Amplifier session.

        Args:
            session_id: The session ID

        Returns:
            True if deleted successfully

        Raises:
            httpx.HTTPError: If the API request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/sessions/{session_id}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return True


# Global client instance
amplifier_client = AmplifierClient()
