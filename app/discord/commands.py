import asyncio

import discord

from app.agents.orchestrator import run_pipeline
from app.discord.bot import bot
from app.utils.logger import setup_logger

logger = setup_logger("discord-commands")

_background_tasks: set["asyncio.Task[None]"] = set()


def _log_if_pipeline_failed(task: "asyncio.Task[None]") -> None:
    _background_tasks.discard(task)
    if not task.cancelled() and task.exception() is not None:
        logger.error("Pipeline run failed.", exc_info=task.exception())


@bot.tree.command(name="generate", description="Generate a new post idea for review.")
async def generate(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Working on it - I will post a draft here shortly.", ephemeral=True)
    task = bot.loop.create_task(run_pipeline())
    _background_tasks.add(task)  # hold a reference so the run isn't garbage-collected mid-way
    task.add_done_callback(_log_if_pipeline_failed)
    