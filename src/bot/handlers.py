"""Message handlers for processing Teams activities."""

from .amplifier_client import amplifier_client
from .bot_adapter import bot_adapter
from .models import TeamsActivity
from .session_manager import session_manager


async def handle_message(activity: TeamsActivity) -> None:
    """Handle incoming message from Teams.

    Args:
        activity: The Teams activity containing the message
    """
    # Extract key information
    conversation_id = activity.conversation["id"]
    user_id = activity.from_["id"]
    text = activity.text or ""
    service_url = activity.serviceUrl

    # Skip empty messages
    if not text.strip():
        return

    # Send typing indicator to show we're processing
    await bot_adapter.send_typing_indicator(service_url, conversation_id)

    try:
        # Get or create session mapping
        session = session_manager.get_session(conversation_id)

        if session is None:
            # Create new Amplifier session
            metadata = {
                "teams_conversation_id": conversation_id,
                "teams_user_id": user_id,
                "source": "teams_bot",
            }
            amplifier_session_id = await amplifier_client.create_session(metadata=metadata)

            # Create mapping
            session = session_manager.create_session(
                conversation_id=conversation_id,
                amplifier_session_id=amplifier_session_id,
                user_id=user_id,
            )
            print(f"Created new session: {amplifier_session_id} for conversation {conversation_id}")
        else:
            # Update activity timestamp
            session_manager.update_activity(conversation_id)

        # Send message to Amplifier
        response = await amplifier_client.send_message(
            session_id=session.amplifier_session_id, content=text
        )

        # Send response back to Teams
        await bot_adapter.send_activity(
            service_url=service_url,
            conversation_id=conversation_id,
            text=response.content,
            reply_to_id=activity.id,
        )

    except Exception as e:
        print(f"Error processing message: {e}")
        # Send error message to user
        error_message = (
            "I encountered an error processing your message. Please try again later."
        )
        await bot_adapter.send_activity(
            service_url=service_url,
            conversation_id=conversation_id,
            text=error_message,
            reply_to_id=activity.id,
        )


async def handle_conversation_update(activity: TeamsActivity) -> None:
    """Handle conversation update events (bot added/removed, members added/removed).

    Args:
        activity: The Teams activity
    """
    # Check if bot was added to conversation
    members_added = activity.value or {}
    if members_added:
        # Send welcome message
        conversation_id = activity.conversation["id"]
        service_url = activity.serviceUrl

        welcome_message = """👋 **Welcome to Amplifier!**

I'm your AI development assistant. You can ask me about:
- Coding questions and best practices
- Architecture and design patterns
- Debugging help
- Code reviews

Just send me a message to get started!"""

        try:
            await bot_adapter.send_activity(
                service_url=service_url, conversation_id=conversation_id, text=welcome_message
            )
        except Exception as e:
            print(f"Error sending welcome message: {e}")


async def handle_invoke(activity: TeamsActivity) -> dict:
    """Handle invoke activities (interactive cards, adaptive cards actions).

    Args:
        activity: The Teams activity

    Returns:
        Response to the invoke
    """
    # For now, just acknowledge
    return {"type": "message", "text": "Action received"}
