from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)  # not used as a context manager here, so the bot never starts


def test_root_and_health_return_ok():
    for path in ("/", "/health"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_lifespan_starts_and_closes_bot(mocker):
    mock_start = mocker.patch("app.main.bot.start", new=AsyncMock())
    mock_close = mocker.patch("app.main.bot.close", new=AsyncMock())

    with TestClient(app):
        pass

    mock_start.assert_awaited_once()
    mock_close.assert_awaited_once()