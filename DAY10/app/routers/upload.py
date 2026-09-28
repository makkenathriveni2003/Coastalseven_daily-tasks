import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.utils.image import resize_image, validate_image

router = APIRouter(prefix="/upload", tags=["Products"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp"}


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided")

    ext = os.path.splitext(file.filename)[1].lower()
    content_type = (file.content_type or "").lower()

    if ext not in ALLOWED_EXT or content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PNG, JPG, JPEG, and WEBP allowed")

    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    file_data = await file.read()
    if not validate_image(file_data):
        raise HTTPException(status_code=400, detail="Invalid image file")

    resized_data = resize_image(file_data)
    safe_name = os.path.basename(file.filename)
    name, _ = os.path.splitext(safe_name)
    unique_name = f"{name}.jpg"
    counter = 1

    while (UPLOAD_DIR / unique_name).exists():
        unique_name = f"{name}_{counter}.jpg"
        counter += 1

    file_path = UPLOAD_DIR / unique_name
    with open(file_path, "wb") as f:
        f.write(resized_data)

    return {
        "filename": unique_name,
        "content_type": content_type,
        "url": f"/uploads/{unique_name}",
        "message": "Image uploaded and resized successfully",
    }
