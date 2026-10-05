from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Day 14 E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

products = [
    {
        "id": 1,
        "name": "Laptop",
        "price": 55000,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853",
    },
    {
        "id": 2,
        "name": "Smartphone",
        "price": 25000,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",
    },
    {
        "id": 3,
        "name": "Headphones",
        "price": 3000,
        "category": "Accessories",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
    },
    {
        "id": 4,
        "name": "Smart Watch",
        "price": 5000,
        "category": "Accessories",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
    },
    {
        "id": 5,
        "name": "Keyboard",
        "price": 2000,
        "category": "Accessories",
        "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3",
    },
    {
        "id": 6,
        "name": "Gaming Mouse",
        "price": 1500,
        "category": "Accessories",
        "image": "https://images.unsplash.com/photo-1527814050087-3793815479db",
    },
    {
        "id": 7,
        "name": "Camera",
        "price": 45000,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32",
    },
    {
        "id": 8,
        "name": "Backpack",
        "price": 2500,
        "category": "Fashion",
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
    },
]


@app.get("/")
def home():
    return {
        "message": "Day 14 FastAPI Backend Running",
        "status": "success",
    }


@app.get("/products")
def get_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return products[skip : skip + limit]


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product

    return {"message": "Product not found"}