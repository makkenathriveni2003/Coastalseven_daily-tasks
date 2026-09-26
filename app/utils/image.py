from io import BytesIO

from PIL import Image, UnidentifiedImageError


def validate_image(file_data: bytes) -> bool:
    if not file_data:
        return False

    try:
        image = Image.open(BytesIO(file_data))
        image.verify()
        return True
    except (UnidentifiedImageError, OSError, ValueError):
        return False


def resize_image(file_data: bytes, size=(300, 300)) -> bytes:
    image = Image.open(BytesIO(file_data))
    converted_image = image.convert("RGB")
    converted_image.thumbnail(size)

    output = BytesIO()
    converted_image.save(output, format="JPEG", quality=85)
    output.seek(0)
    return output.getvalue()
