from unittest.mock import AsyncMock, MagicMock

import pytest

from app.discord.views import ApprovalDecision, PostApprovalView


def _make_interaction():
    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()
    return interaction


def _button(view, label):
    return next(child for child in view.children if getattr(child, "label", None) == label)


@pytest.mark.asyncio
async def test_accept_sets_decision_and_disables_buttons():
    view = PostApprovalView()
    interaction = _make_interaction()

    await _button(view, "Accept").callback(interaction)

    assert view.decision == ApprovalDecision.ACCEPTED
    assert all(child.disabled for child in view.children)
    interaction.response.edit_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_reject_sets_decision():
    view = PostApprovalView()
    interaction = _make_interaction()

    await _button(view, "Reject").callback(interaction)

    assert view.decision == ApprovalDecision.REJECTED



@pytest.mark.asyncio
async def test_retry_sets_decision():
    view = PostApprovalView()
    await _button(view, "Re-try").callback(_make_interaction())
    assert view.decision == ApprovalDecision.RETRY


@pytest.mark.asyncio
async def test_wait_for_decision_returns_after_button_press():
    view = PostApprovalView()
    await _button(view, "Accept").callback(_make_interaction())

    decision = await view.wait_for_decision()

    assert decision == ApprovalDecision.ACCEPTED


@pytest.mark.asyncio
async def test_on_timeout_defaults_to_rejected_and_edits_message():
    view = PostApprovalView()
    view.message = MagicMock()
    view.message.edit = AsyncMock()

    await view.on_timeout()

    assert view.decision == ApprovalDecision.REJECTED
    assert all(child.disabled for child in view.children)
    view.message.edit.assert_awaited_once()


@pytest.mark.asyncio
async def test_on_timeout_without_message_does_not_raise():
    view = PostApprovalView()
    view.message = None

    await view.on_timeout()

    assert view.decision == ApprovalDecision.REJECTED
