from unittest.mock import AsyncMock, MagicMock

import pytest

from app.discord.commands import generate


@pytest.mark.asyncio
async def test_generate_command_acks_and_schedules_pipeline(mocker):
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()

    mock_bot = mocker.patch("app.discord.commands.bot")
    mocker.patch("app.discord.commands.run_pipeline", new=MagicMock(return_value="coro-placeholder"))

    await generate.callback(interaction)

    interaction.response.send_message.assert_awaited_once()
    mock_bot.loop.create_task.assert_called_once_with("coro-placeholder")