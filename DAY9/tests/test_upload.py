from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_valid_image_bytes() -> bytes:
    from PIL import Image

    image = Image.new("RGB", (100, 100), color="blue")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_root_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200


def test_upload_valid_image() -> None:
    response = client.post(
        "/upload/",
        files={"file": ("test.png", create_valid_image_bytes(), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"].endswith(".png")
    assert payload["url"].startswith("/uploads/")


def test_upload_invalid_file() -> None:
    response = client.post(
        "/upload/",
        files={"file": ("bad.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 400
    assert "Only" in response.json()["detail"]
