"""Data models for the Teams Bot."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TeamsActivity(BaseModel):
    """Represents an incoming Teams activity/message."""

    type: str = Field(..., description="Activity type (e.g., 'message', 'conversationUpdate')")
    id: str = Field(..., description="Activity ID")
    timestamp: datetime = Field(..., description="When the activity was sent")
    serviceUrl: str = Field(..., description="Service URL for sending responses")
    channelId: str = Field(..., description="Channel identifier (e.g., 'msteams')")
    from_: dict = Field(..., alias="from", description="Sender information")
    conversation: dict = Field(..., description="Conversation information")
    recipient: dict = Field(..., description="Bot recipient information")
    text: Optional[str] = Field(None, description="Message text content")
    textFormat: Optional[str] = Field(None, description="Text format (plain, markdown, xml)")
    attachments: Optional[list[dict]] = Field(None, description="Message attachments")
    entities: Optional[list[dict]] = Field(None, description="Activity entities")
    channelData: Optional[dict] = Field(None, description="Channel-specific data")
    action: Optional[str] = Field(None, description="Action for invoke activities")
    replyToId: Optional[str] = Field(None, description="ID of activity this is replying to")
    value: Optional[dict] = Field(None, description="Additional activity value")
    name: Optional[str] = Field(None, description="Activity name")
    relatesTo: Optional[dict] = Field(None, description="Related conversation reference")
    code: Optional[str] = Field(None, description="End of conversation code")
    expiration: Optional[datetime] = Field(None, description="When activity expires")
    importance: Optional[str] = Field(None, description="Activity importance")
    deliveryMode: Optional[str] = Field(None, description="Delivery mode")
    listenFor: Optional[list[str]] = Field(None, description="Listen for phrases")
    textHighlights: Optional[list[dict]] = Field(None, description="Text highlights")
    semanticAction: Optional[dict] = Field(None, description="Semantic action")

    class Config:
        populate_by_name = True


class SessionMapping(BaseModel):
    """Maps Teams conversation to Amplifier session."""

    conversation_id: str = Field(..., description="Teams conversation ID")
    amplifier_session_id: str = Field(..., description="Amplifier session ID")
    user_id: str = Field(..., description="Teams user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0, description="Number of messages in this session")


class AmplifierSessionRequest(BaseModel):
    """Request to create an Amplifier session."""

    base_config_id: str = Field(..., description="Base configuration ID")
    base_config_name: str = Field(..., description="Base configuration name")
    metadata: Optional[dict[str, Any]] = Field(
        None, description="Additional session metadata"
    )


class AmplifierMessageRequest(BaseModel):
    """Request to send a message to an Amplifier session."""

    content: str = Field(..., description="Message content to send")


class AmplifierMessageResponse(BaseModel):
    """Response from Amplifier session message."""

    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None
