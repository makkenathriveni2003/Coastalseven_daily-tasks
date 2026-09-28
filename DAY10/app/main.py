from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.models import Product, User  # noqa: F401
from app.routers.auth import router as auth_router
from app.routers.cart import router as cart_router
from app.routers.orders import router as order_router
from app.routers.products import router as products_router
from app.routers.upload import router as upload_router
from app.routers.websocket import router as websocket_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce API", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/uploads", StaticFiles(directory=BASE_DIR / "uploads"), name="uploads")
app.mount("/store", StaticFiles(directory=BASE_DIR / "frontend", html=True), name="store")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(upload_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(websocket_router)


@app.get("/")
def root():
    return {"message": "Ecommerce API is running"}


@app.get("/store")
def store():
    return FileResponse(BASE_DIR / "frontend" / "index.html")
