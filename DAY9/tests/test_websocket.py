from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_websocket_echo() -> None:
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text("hello")
        data = websocket.receive_text()
        assert data == "Server received: hello"
