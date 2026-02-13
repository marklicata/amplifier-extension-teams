"""Bot adapter for handling Teams activities and sending responses."""

import httpx

from .config import settings
from .models import TeamsActivity


class BotAdapter:
    """Handles Teams Bot Framework protocol for sending messages."""

    def __init__(self):
        """Initialize the bot adapter."""
        self.app_id = settings.microsoft_app_id
        self.app_password = settings.microsoft_app_password
        self.app_type = settings.microsoft_app_type
        self.app_tenant_id = getattr(settings, 'microsoft_app_tenant_id', None)

    async def send_activity(
        self, service_url: str, conversation_id: str, text: str, reply_to_id: str | None = None
    ):
        """Send a message back to Teams.

        Args:
            service_url: Service URL from the incoming activity
            conversation_id: Conversation ID to send to
            text: Message text to send
            reply_to_id: Optional activity ID to reply to
        """
        # Build the reply activity
        activity = {
            "type": "message",
            "from": {"id": self.app_id, "name": "Amplifier"},
            "conversation": {"id": conversation_id},
            "text": text,
            "textFormat": "markdown",
        }

        if reply_to_id:
            activity["replyToId"] = reply_to_id

        # Get access token for Bot Framework
        token = await self._get_access_token()

        # Send to Teams
        url = f"{service_url.rstrip('/')}/v3/conversations/{conversation_id}/activities"
        if reply_to_id:
            url += f"/{reply_to_id}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=activity, timeout=30.0)
            response.raise_for_status()

    async def _get_access_token(self) -> str:
        """Get Bot Framework access token from Microsoft.

        Returns:
            Access token for Bot Framework API calls

        Raises:
            httpx.HTTPError: If token request fails
        """
        # Use tenant-specific endpoint for SingleTenant bots
        if self.app_type == "SingleTenant" and self.app_tenant_id:
            url = f"https://login.microsoftonline.com/{self.app_tenant_id}/oauth2/v2.0/token"
        else:
            url = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.app_id,
            "client_secret": self.app_password,
            "scope": "https://api.botframework.com/.default",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, timeout=10.0)
            response.raise_for_status()
            token_data = response.json()
            return token_data["access_token"]

    async def send_typing_indicator(self, service_url: str, conversation_id: str):
        """Send typing indicator to show bot is processing.

        Args:
            service_url: Service URL from the incoming activity
            conversation_id: Conversation ID
        """
        activity = {
            "type": "typing",
            "from": {"id": self.app_id},
            "conversation": {"id": conversation_id},
        }

        token = await self._get_access_token()
        url = f"{service_url.rstrip('/')}/v3/conversations/{conversation_id}/activities"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, headers=headers, json=activity, timeout=10.0)
            except Exception as e:
                # Typing indicators are best-effort, don't fail if they don't work
                print(f"Failed to send typing indicator: {e}")


# Global adapter instance
bot_adapter = BotAdapter()
