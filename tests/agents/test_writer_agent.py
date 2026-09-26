import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agents import writer_agent
from app.discord.views import ApprovalDecision


class _FakeTopic:
    def __init__(self, title="Caching Strategies", description="description"):
        self.title = title
        self.description = description


SAMPLE_POSTS = [
    {"platform": "LinkedIn", "post_content": "LinkedIn body"},
    # {"platform": "X", "post_content": "X body"},  # Uncomment - If added credits on X platform.
]


def test_draft_post_returns_validated_posts(mocker):
    fake_response = mocker.Mock(text=json.dumps(SAMPLE_POSTS))
    mock_client = mocker.Mock()
    mock_client.models.generate_content.return_value = fake_response
    mocker.patch("app.agents.writer_agent.get_client", return_value=mock_client)

    result = writer_agent._draft_post(_FakeTopic())

    assert result == SAMPLE_POSTS


def test_draft_post_raises_on_wrong_item_count(mocker):
    fake_response = mocker.Mock(text=json.dumps(SAMPLE_POSTS + SAMPLE_POSTS))
    mock_client = mocker.Mock()
    mock_client.models.generate_content.return_value = fake_response
    mocker.patch("app.agents.writer_agent.get_client", return_value=mock_client)

    with pytest.raises(ValueError):
        writer_agent._draft_post(_FakeTopic())


def test_draft_post_raises_on_non_string_platform(mocker):
    bad_posts = [{"platform": 123, "post_content": "X"}]
    fake_response = mocker.Mock(text=json.dumps(bad_posts))
    mock_client = mocker.Mock()
    mock_client.models.generate_content.return_value = fake_response
    mocker.patch("app.agents.writer_agent.get_client", return_value=mock_client)

    with pytest.raises(TypeError):
        writer_agent._draft_post(_FakeTopic())


@pytest.mark.asyncio
async def test_generate_post_returns_approved_post_on_accept(mocker):
    mocker.patch("app.agents.writer_agent._draft_post", return_value=SAMPLE_POSTS)
    mocker.patch("app.agents.writer_agent.send_for_approval", new=AsyncMock(return_value=MagicMock()))

    fake_view = MagicMock()
    fake_view.wait_for_decision = AsyncMock(return_value=ApprovalDecision.ACCEPTED)
    mocker.patch("app.agents.writer_agent.PostApprovalView", return_value=fake_view)

    result = await writer_agent.generate_post(_FakeTopic())

    assert result is not None
    assert result.linkedin_content == "LinkedIn body"
    # assert result.x_content == "X body"   # Uncomment - If added credits on X platform.


@pytest.mark.asyncio
async def test_generate_post_returns_none_on_reject(mocker):
    mocker.patch("app.agents.writer_agent._draft_post", return_value=SAMPLE_POSTS)
    mocker.patch("app.agents.writer_agent.send_for_approval", new=AsyncMock(return_value=MagicMock()))

    fake_view = MagicMock()
    fake_view.wait_for_decision = AsyncMock(return_value=ApprovalDecision.REJECTED)
    mocker.patch("app.agents.writer_agent.PostApprovalView", return_value=fake_view)

    result = await writer_agent.generate_post(_FakeTopic())

    assert result is None


@pytest.mark.asyncio
async def test_generate_post_redrafts_on_retry_then_accepts(mocker):
    mock_draft = mocker.patch("app.agents.writer_agent._draft_post", return_value=SAMPLE_POSTS)
    mocker.patch("app.agents.writer_agent.send_for_approval", new=AsyncMock(return_value=MagicMock()))

    first_view = MagicMock()
    first_view.wait_for_decision = AsyncMock(return_value=ApprovalDecision.RETRY)
    second_view = MagicMock()
    second_view.wait_for_decision = AsyncMock(return_value=ApprovalDecision.ACCEPTED)
    mocker.patch("app.agents.writer_agent.PostApprovalView", side_effect=[first_view, second_view])

    result = await writer_agent.generate_post(_FakeTopic())

    assert result is not None
    assert result.linkedin_content == "LinkedIn body"
    assert mock_draft.call_count == 2


@pytest.mark.asyncio
async def test_generate_post_raises_when_topic_title_is_none():
    with pytest.raises(ValueError):
        await writer_agent.generate_post(_FakeTopic(title=None))
