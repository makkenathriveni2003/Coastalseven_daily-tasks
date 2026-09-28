from io import BytesIO

from PIL import Image
import pytest
from starlette.websockets import WebSocketDisconnect


def test_upload_image_success(client):
    image = Image.new("RGB", (100, 100), color="blue")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/upload/",
        files={"file": ("avatar.png", buffer.read(), "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"].endswith(".jpg") or body["filename"].endswith(".jpeg")
    assert body["content_type"] == "image/png"
    assert body["url"].startswith("/uploads/")


def test_upload_rejects_invalid_image(client):
    response = client.post(
        "/upload/",
        files={"file": ("bad.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] in {"Only PNG, JPG, JPEG, and WEBP allowed", "Only image files are allowed", "Invalid image file"}


def test_websocket_requires_authentication(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws"):
            pass
