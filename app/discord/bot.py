import discord
from discord.ext import commands

from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("discord-bot")

intents = discord.Intents.default()  # slash commands only — no privileged intents needed
bot = commands.Bot(command_prefix="!", intents=intents)


async def send_for_approval(embed: discord.Embed, view: discord.ui.View) -> discord.Message:
    """Post a draft + its Accept/Reject/Re-try buttons to the approval channel."""
    channel = bot.get_channel(settings.DISCORD_APPROVAL_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(settings.DISCORD_APPROVAL_CHANNEL_ID)

    if not isinstance(channel, discord.abc.Messageable):
        raise TypeError(
            f"Approval channel must be messageable, got {type(channel).__name__}"
        )
    
    return await channel.send(embed=embed, view=view)


_startup_done = False  # on_ready can fire again after a reconnect; startup work must run once


@bot.event
async def on_ready() -> None:
    global _startup_done
    if _startup_done:
        return
    _startup_done = True

    # Deferred import - avoids a circular import, since scheduler/jobs.py pulls in
    # orchestrator.py -> writer_agent.py, which imports send_for_approval from this module.
    from app.scheduler.jobs import start_scheduler

    logger.info("Discord bot logged in as %s", bot.user)

    guild = discord.Object(id=settings.DISCORD_SERVER_ID)
    bot.tree.copy_global_to(guild=guild)
    try:
        synced = await bot.tree.sync(guild=guild)
        logger.info("Synced %d slash command(s) to guild %s", len(synced), settings.DISCORD_SERVER_ID)
    except discord.HTTPException:
        # No retry: repeated failed calls make a rate limit worse. Commands synced earlier
        # stay registered in Discord, and the scheduler below must still start.
        logger.exception("Could not sync slash commands.")

    start_scheduler()


def run_discord_bot() -> None:
    # Imported here, not at the top, to avoid a circular import (commands.py imports this
    # module). This import is what registers /generate.
    from app.discord import commands as _commands  # noqa: F401

    bot.run(settings.DISCORD_BOT_TOKEN)
