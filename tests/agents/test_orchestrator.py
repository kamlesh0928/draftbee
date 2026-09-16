import pytest

from app.agents import orchestrator
from app.database.models.topic import STATUS_REJECTED, STATUS_USED


class _FakeTopic:
    def __init__(self, id, title="Idea", rank=1):
        self.id = id
        self.title = title
        self.rank = rank


@pytest.mark.asyncio
async def test_run_pipeline_stops_on_first_accepted_topic(mocker):
    topics = [_FakeTopic(id=1), _FakeTopic(id=2)]
    mocker.patch("app.agents.orchestrator.get_topics", return_value=topics)
    mock_generate_post = mocker.patch("app.agents.orchestrator.generate_post", side_effect=[True])
    mock_mark_status = mocker.patch("app.agents.orchestrator.mark_topic_status")

    await orchestrator.run_pipeline()

    mock_generate_post.assert_awaited_once_with(topics[0])
    mock_mark_status.assert_called_once_with(1, STATUS_USED)


@pytest.mark.asyncio
async def test_run_pipeline_tries_next_topic_after_rejection(mocker):
    topics = [_FakeTopic(id=1), _FakeTopic(id=2)]
    mocker.patch("app.agents.orchestrator.get_topics", return_value=topics)
    mocker.patch("app.agents.orchestrator.generate_post", side_effect=[False, True])
    mock_mark_status = mocker.patch("app.agents.orchestrator.mark_topic_status")

    await orchestrator.run_pipeline()

    assert mock_mark_status.call_args_list == [
        mocker.call(1, STATUS_REJECTED),
        mocker.call(2, STATUS_USED),
    ]


@pytest.mark.asyncio
async def test_run_pipeline_regenerates_when_all_topics_rejected(mocker):
    first_batch = [_FakeTopic(id=1)]
    second_batch = [_FakeTopic(id=2)]
    mock_get_topics = mocker.patch("app.agents.orchestrator.get_topics", side_effect=[first_batch, second_batch])
    mocker.patch("app.agents.orchestrator.generate_post", side_effect=[False, True])
    mocker.patch("app.agents.orchestrator.mark_topic_status")

    await orchestrator.run_pipeline()

    assert mock_get_topics.call_count == 2


@pytest.mark.asyncio
async def test_run_pipeline_asserts_topic_must_be_persisted(mocker):
    mocker.patch("app.agents.orchestrator.get_topics", return_value=[_FakeTopic(id=None)])
    mocker.patch("app.agents.orchestrator.generate_post")

    with pytest.raises(AssertionError):
        await orchestrator.run_pipeline()
