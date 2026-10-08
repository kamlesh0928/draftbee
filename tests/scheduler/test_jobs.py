import pytest

from app.scheduler import jobs


@pytest.mark.asyncio
async def test_scheduled_run_calls_run_pipeline(mocker):
    mock_run_pipeline = mocker.patch("app.scheduler.jobs.run_pipeline", new=mocker.AsyncMock())

    await jobs._scheduled_run()

    mock_run_pipeline.assert_awaited_once()


def test_start_scheduler_is_idempotent(mocker):
    mocker.patch.object(jobs._scheduler, "running", False)
    mock_add_job = mocker.patch.object(jobs._scheduler, "add_job")
    mock_start = mocker.patch.object(jobs._scheduler, "start")

    jobs.start_scheduler()

    mock_add_job.assert_called_once()
    mock_start.assert_called_once()


def test_start_scheduler_does_nothing_if_already_running(mocker):
    mocker.patch.object(jobs._scheduler, "running", True)
    mock_add_job = mocker.patch.object(jobs._scheduler, "add_job")

    jobs.start_scheduler()

    mock_add_job.assert_not_called()