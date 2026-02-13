"""Run the Amplifier Teams Bot server."""

import uvicorn

from src.bot.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.bot.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level="info",
    )
