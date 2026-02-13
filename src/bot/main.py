"""Main FastAPI application for the Amplifier Teams Bot."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from .config import settings
from .handlers import handle_conversation_update, handle_invoke, handle_message
from .models import TeamsActivity
from .session_manager import session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    print("Starting Amplifier Teams Bot...")
    print(f"Amplifier API: {settings.amplifier_api_url}")
    print(f"Bot Service URL: {settings.bot_service_url}")
    await session_manager.start()

    yield

    # Shutdown
    print("Shutting down...")
    await session_manager.stop()


app = FastAPI(
    title="Amplifier Teams Bot",
    description="Teams Bot for direct Amplifier integration",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "amplifier-teams-bot",
        "version": "0.1.0",
        "active_sessions": session_manager.get_session_count(),
    }


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.post("/api/messages")
async def messages(request: Request):
    """Main webhook endpoint for Teams Bot Framework.

    This receives all activities from Teams (messages, events, etc.)
    """
    try:
        # Parse incoming activity
        body = await request.json()
        activity = TeamsActivity(**body)

        # Route based on activity type
        if activity.type == "message":
            await handle_message(activity)
            return JSONResponse(status_code=status.HTTP_200_OK, content={})

        elif activity.type == "conversationUpdate":
            await handle_conversation_update(activity)
            return JSONResponse(status_code=status.HTTP_200_OK, content={})

        elif activity.type == "invoke":
            result = await handle_invoke(activity)
            return JSONResponse(status_code=status.HTTP_200_OK, content=result)

        else:
            # Unknown activity type - just acknowledge
            print(f"Received unknown activity type: {activity.type}")
            return JSONResponse(status_code=status.HTTP_200_OK, content={})

    except Exception as e:
        print(f"Error processing activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions (for debugging/monitoring)."""
    return {
        "total_sessions": session_manager.get_session_count(),
        "sessions": [
            {
                "conversation_id": s.conversation_id,
                "amplifier_session_id": s.amplifier_session_id,
                "user_id": s.user_id,
                "message_count": s.message_count,
                "last_activity": s.last_activity.isoformat(),
            }
            for s in session_manager._sessions.values()
        ],
    }


@app.delete("/api/sessions/{conversation_id}")
async def delete_session(conversation_id: str):
    """Delete a session mapping (for debugging/admin)."""
    deleted = session_manager.delete_session(conversation_id)
    if deleted:
        return {"status": "deleted", "conversation_id": conversation_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")
