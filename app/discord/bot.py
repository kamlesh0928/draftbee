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


@bot.event
async def on_ready() -> None:
    guild = discord.Object(id=settings.DISCORD_SERVER_ID)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    logger.info("Synced %d slash command(s) to guild %s", len(synced), settings.DISCORD_SERVER_ID)
    logger.info("Discord bot logged in as %s", bot.user)


def run_discord_bot() -> None:
    from app.discord import (
        commands as _commands,  # noqa: F401 — registers /generate via decorator
    )

    bot.run(settings.DISCORD_BOT_TOKEN)
