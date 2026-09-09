import json
import pytest

from app.discovery.feeds import discover_topics

SAMPLE_RESPONSE = json.dumps([
    {
        "title": f"Idea {i}", 
        "description": "Description of idea {i}", 
        "rank": i, 
        "explanation": "Explanation of ides {i}"
    }
    for i in range(1, 6)
])

def test_discover_topics_returns_all_five_sorted(mocker):
    fake_response = mocker.Mock()
    fake_response.text = SAMPLE_RESPONSE

    mock_client = mocker.Mock()
    mock_client.models.generate_content.return_value = fake_response
    mocker.patch("app.discovery.feeds.genai.Client", return_value=mock_client)

    result = discover_topics()

    assert len(result) == 5
    assert result[0]["rank"] == 1 

def test_discover_topics_raises_on_invalid_json(mocker):
    fake_response = mocker.Mock()
    fake_response.text = "not valid json"

    mock_client = mocker.Mock()
    mock_client.models.generate_content.return_value = fake_response
    mocker.patch("app.discovery.feeds.genai.Client", return_value=mock_client)

    with pytest.raises(ValueError):
        discover_topics()
