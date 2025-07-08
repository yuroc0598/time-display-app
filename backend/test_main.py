from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_time_api_endpoint():
    response = client.get("/api/time")
    assert response.status_code == 200
    data = response.json()
    assert "current_time" in data
    assert isinstance(data["current_time"], str)
    assert len(data["current_time"]) > 0


def test_time_format():
    response = client.get("/api/time")
    data = response.json()
    time_str = data["current_time"]
    # Check if format is YYYY-MM-DD HH:MM:SS
    assert len(time_str) == 19
    assert time_str[4] == "-"
    assert time_str[7] == "-"
    assert time_str[10] == " "
    assert time_str[13] == ":"
    assert time_str[16] == ":"