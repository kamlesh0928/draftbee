from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from app.discord import bot as bot_module


@pytest.mark.asyncio
async def test_send_for_approval_uses_cached_channel(mocker):
    fake_channel = MagicMock(spec=discord.abc.Messageable)
    fake_channel.send = AsyncMock(return_value="sent-message")
    mocker.patch.object(bot_module.bot, "get_channel", return_value=fake_channel)
    mock_fetch = mocker.patch.object(bot_module.bot, "fetch_channel", new=AsyncMock())

    result = await bot_module.send_for_approval(MagicMock(), MagicMock())

    assert result == "sent-message"
    mock_fetch.assert_not_called()


@pytest.mark.asyncio
async def test_send_for_approval_falls_back_to_fetch_channel(mocker):
    fake_channel = MagicMock(spec=discord.abc.Messageable)
    fake_channel.send = AsyncMock(return_value="sent-message")
    mocker.patch.object(bot_module.bot, "get_channel", return_value=None)
    mocker.patch.object(bot_module.bot, "fetch_channel", new=AsyncMock(return_value=fake_channel))

    result = await bot_module.send_for_approval(MagicMock(), MagicMock())

    assert result == "sent-message"


@pytest.mark.asyncio
async def test_send_for_approval_rejects_non_messageable_channel(mocker):
    fake_channel = MagicMock(spec=discord.CategoryChannel)
    mocker.patch.object(bot_module.bot, "get_channel", return_value=fake_channel)

    with pytest.raises(TypeError):
        await bot_module.send_for_approval(MagicMock(), MagicMock())


@pytest.mark.asyncio
async def test_on_ready_syncs_once_and_starts_scheduler(mocker):
    bot_module._startup_done = False
    mock_sync = mocker.patch.object(bot_module.bot.tree, "sync", new=AsyncMock(return_value=[]))
    mock_start = mocker.patch("app.scheduler.jobs.start_scheduler")

    await bot_module.on_ready()
    await bot_module.on_ready()  # a reconnect fires on_ready again

    mock_sync.assert_awaited_once()
    mock_start.assert_called_once()


@pytest.mark.asyncio
async def test_on_ready_still_starts_scheduler_if_sync_fails(mocker):
    bot_module._startup_done = False
    response = MagicMock(status=429, reason="Too Many Requests")
    mocker.patch.object(
        bot_module.bot.tree, "sync", new=AsyncMock(side_effect=discord.HTTPException(response, "rate limited"))
    )
    mock_start = mocker.patch("app.scheduler.jobs.start_scheduler")

    await bot_module.on_ready()

    mock_start.assert_called_once()
    