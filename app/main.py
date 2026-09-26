from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers.upload import router as upload_router
from app.routers.websocket import router as websocket_router

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Day 9 FastAPI")

UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(upload_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")
