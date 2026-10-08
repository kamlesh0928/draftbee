"""
Cron-style scheduling for the content pipeline.

Runs run_pipeline() automatically every 1 days, independent of the
on-demand /generate Discord command (app/discord/commands.py) - both
trigger the exact same pipeline, just on a different schedule.
"""

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.agents.orchestrator import run_pipeline
from app.utils.logger import setup_logger

logger = setup_logger("scheduler")

_scheduler = AsyncIOScheduler()


async def _scheduled_run() -> None:
    logger.info("Scheduled run starting.")
    await run_pipeline()


def start_scheduler() -> None:
    """
    Start the every-1-days posting job, tied to the bot's own event loop.

    Call this from on_ready() (after the bot is connected) - AsyncIOScheduler
    needs a running event loop to start against. Safe to call more than once
    (Discord can fire on_ready again after a reconnect); does nothing if the
    scheduler is already running, so it won't register duplicate jobs.
    """

    if _scheduler.running:
        return

    _scheduler.add_job(
        _scheduled_run,
        trigger=IntervalTrigger(days=1),
        id="post-every-1-day",
        # Fires once immediately on startup, then every 1 days after that.
        # Remove `next_run_time` if you'd rather wait a full 1 days before the first post.
        next_run_time=datetime.now(),
        replace_existing=True,
        max_instances=1,  # skip a run if the previous one is still in progress
    )

    _scheduler.start()
    logger.info("Scheduler started - a new post will be generated every 1 days.")
