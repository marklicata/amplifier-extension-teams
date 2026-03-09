"""Bot adapter with managed identity authentication."""

import httpx
from datetime import datetime, timedelta
from azure.identity.aio import DefaultAzureCredential

from .config import settings


class BotAdapter:
    """Handles Teams Bot Framework protocol with managed identity auth."""

    def __init__(self):
        """Initialize the bot adapter with managed identity."""
        self.app_id = settings.microsoft_app_id
        
        # Use Azure Managed Identity (works in Azure Container Apps)
        self.credential = DefaultAzureCredential()
        
        # Token cache
        self._token_cache = None
        self._token_expiry = None

    async def send_activity(
        self, service_url: str, conversation_id: str, text: str, reply_to_id: str | None = None
    ):
        """Send a message back to Teams."""
        activity = {
            "type": "message",
            "from": {"id": self.app_id, "name": "Amplifier"},
            "conversation": {"id": conversation_id},
            "text": text,
            "textFormat": "markdown",
        }

        if reply_to_id:
            activity["replyToId"] = reply_to_id

        token = await self._get_access_token()

        # Fixed: replyToId in body, not URL
        url = f"{service_url.rstrip('/')}/v3/conversations/{conversation_id}/activities"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=activity, timeout=30.0)
            response.raise_for_status()

    async def _get_access_token(self) -> str:
        """Get Bot Framework token using managed identity."""
        
        # Return cached token if still valid
        if self._token_cache and self._token_expiry:
            if datetime.utcnow() < self._token_expiry:
                return self._token_cache
        
        # Get token using managed identity
        token = await self.credential.get_token("https://api.botframework.com/.default")
        
        # Cache token
        self._token_cache = token.token
        self._token_expiry = datetime.fromtimestamp(token.expires_on) - timedelta(seconds=300)
        
        return self._token_cache

    async def send_typing_indicator(self, service_url: str, conversation_id: str):
        """Send typing indicator."""
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
                print(f"Failed to send typing indicator: {e}")


bot_adapter = BotAdapter()
