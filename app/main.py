import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.settings import settings
from app.discord import commands as _commands  # noqa: F401 - registers the /generate command
from app.discord.bot import bot
from app.utils.logger import setup_logger

logger = setup_logger("web")


def _log_if_bot_crashed(task: "asyncio.Task[None]") -> None:
    """The bot runs as a background task, so surface its failure in the logs instead of losing it."""
    if not task.cancelled() and task.exception() is not None:
        logger.error("Discord bot stopped unexpectedly.", exc_info=task.exception())


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    bot_task = asyncio.create_task(bot.start(settings.DISCORD_BOT_TOKEN))
    bot_task.add_done_callback(_log_if_bot_crashed)
    try:
        yield
    finally:
        await bot.close()
        await asyncio.gather(bot_task, return_exceptions=True)


app = FastAPI(title="DraftBee", lifespan=lifespan)


@app.get("/")
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}