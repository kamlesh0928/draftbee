from app.agents import gemini_client


def test_get_client_returns_cached_singleton(mocker):
    gemini_client.get_client.cache_clear()
    mock_ctor = mocker.patch("app.agents.gemini_client.genai.Client")

    first = gemini_client.get_client()
    second = gemini_client.get_client()

    assert first is second
    mock_ctor.assert_called_once()
