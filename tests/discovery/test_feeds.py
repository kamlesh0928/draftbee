import json

from app.discovery import feeds

SAMPLE_RESPONSE = json.dumps(
    [
        {
            "title": f"Idea {i}", 
            "description": f"Description {i}", 
            "rank": i, 
            "explanation": f"Why {i}"
        }
        for i in range(1, 6)
    ]
)


def test_generate_topic_ideas_returns_all_five_sorted(mocker):
    fake_response = mocker.Mock(text=SAMPLE_RESPONSE)
    mock_client = mocker.Mock()
    mock_client.models.generate_content.return_value = fake_response
    mocker.patch("app.discovery.feeds.get_client", return_value=mock_client)

    result = feeds._generate_topic_ideas()

    assert len(result) == 5
    assert result[0]["rank"] == 1


def test_get_topics_uses_db_cache_when_available(mocker):
    cached = [mocker.Mock(rank=1)]
    mocker.patch("app.discovery.feeds.get_pending_topics", return_value=cached)
    mock_generate = mocker.patch("app.discovery.feeds._generate_topic_ideas")

    result = feeds.get_topics()

    assert result == cached
    mock_generate.assert_not_called()  # proves we skipped calling Gemini


def test_get_topics_falls_back_to_ai_when_cache_empty(mocker):
    mocker.patch("app.discovery.feeds.get_pending_topics", return_value=[])
    mocker.patch("app.discovery.feeds._generate_topic_ideas", return_value=["fake-idea"])
    mock_save = mocker.patch("app.discovery.feeds.save_topics", return_value=["saved-idea"])

    result = feeds.get_topics()

    assert result == ["saved-idea"]
    mock_save.assert_called_once_with(["fake-idea"])