import pytest

from app.scheduler import jobs


@pytest.mark.asyncio
async def test_scheduled_run_calls_run_pipeline(mocker):
    mock_run_pipeline = mocker.patch("app.scheduler.jobs.run_pipeline", new=mocker.AsyncMock())

    await jobs._scheduled_run()

    mock_run_pipeline.assert_awaited_once()


def test_start_scheduler_is_idempotent(mocker):
    mock_scheduler = mocker.patch.object(jobs, "_scheduler")
    mock_scheduler.running = False

    jobs.start_scheduler()

    mock_scheduler.add_job.assert_called_once()
    mock_scheduler.start.assert_called_once()


def test_start_scheduler_does_nothing_if_already_running(mocker):
    mock_scheduler = mocker.patch.object(jobs, "_scheduler")
    mock_scheduler.running = True

    jobs.start_scheduler()

    mock_scheduler.add_job.assert_not_called()