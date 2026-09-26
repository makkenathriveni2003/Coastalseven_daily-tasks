import os
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.utils.image import validate_image, resize_image

router = APIRouter(prefix="/upload", tags=["File Upload"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided")

    extension = os.path.splitext(file.filename)[1].lower()
    content_type = (file.content_type or "").lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PNG, JPG, JPEG, and WEBP files are allowed",
        )

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400, detail="Only exact image MIME types are allowed"
        )

    file_data = await file.read()

    if not validate_image(file_data):
        raise HTTPException(status_code=400, detail="Invalid image file")

    resized_data = resize_image(file_data)

    safe_name = os.path.basename(file.filename)
    unique_name = safe_name
    counter = 1

    while (UPLOAD_DIR / unique_name).exists():
        name, ext = os.path.splitext(safe_name)
        unique_name = f"{name}_{counter}{ext}"
        counter += 1

    file_path = UPLOAD_DIR / unique_name

    with open(file_path, "wb") as image_file:
        image_file.write(resized_data)

    return {
        "filename": unique_name,
        "content_type": file.content_type,
        "original_size": len(file_data),
        "resized_size": len(resized_data),
        "message": "Image validated and resized successfully",
        "url": f"/uploads/{unique_name}",
    }
