import os
from io import BytesIO

from PIL import Image


def validate_image(file_data: bytes) -> bool:
    try:
        img = Image.open(BytesIO(file_data))
        img.verify()
        return True
    except Exception:
        return False


def resize_image(file_data: bytes, max_size=(1200, 1200)) -> bytes:
    img = Image.open(BytesIO(file_data)).convert("RGB")
    img.thumbnail(max_size)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()
