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
