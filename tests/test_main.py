from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_ok_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Server is running on Port 5001"}