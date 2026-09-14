import discord

from app.agents.orchestrator import run_pipeline
from app.discord.bot import bot
from app.utils.logger import setup_logger

logger = setup_logger("discord-commands")


@bot.tree.command(name="generate", description="Generate a new post idea for review.")
async def generate(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Working on it - I will post a draft here shortly.", ephemeral=True)
    bot.loop.create_task(run_pipeline())
