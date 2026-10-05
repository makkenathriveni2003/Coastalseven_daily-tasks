from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Day 15 E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
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
    {
        "id": 9,
        "name": "Floral Midi Dress",
        "price": 4200,
        "category": "Dresses",
        "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8",
    },
    {
        "id": 10,
        "name": "Satin Evening Dress",
        "price": 6800,
        "category": "Dresses",
        "image": "https://images.unsplash.com/photo-1566174053879-31528523f8ae",
    },
    {
        "id": 11,
        "name": "Linen Summer Dress",
        "price": 5100,
        "category": "Dresses",
        "image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea",
    },
    {
        "id": 12,
        "name": "Pearl Drop Earrings",
        "price": 1800,
        "category": "Jewelry",
        "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908",
    },
    {
        "id": 13,
        "name": "Gold Layered Necklace",
        "price": 2400,
        "category": "Jewelry",
        "image": "https://images.unsplash.com/photo-1611652022419-a9419f74343d",
    },
    {
        "id": 14,
        "name": "Everyday Gold Hoops",
        "price": 1500,
        "category": "Jewelry",
        "image": "https://images.unsplash.com/photo-1617038220319-276d3cfab638",
    },
    {
        "id": 15,
        "name": "Film Night Graphic Tee",
        "price": 1200,
        "category": "Shirts",
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab",
    },
    {
        "id": 16,
        "name": "Sunrise Story Graphic Tee",
        "price": 1400,
        "category": "Shirts",
        "image": "https://images.unsplash.com/photo-1576566588028-4147f3842f27",
    },
    {
        "id": 17,
        "name": "Midnight Premiere Tee",
        "price": 1600,
        "category": "Shirts",
        "image": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c",
    },
]


@app.get("/")
def home():
    return {
        "message": "Day 15 FastAPI Backend Running",
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

    raise HTTPException(status_code=404, detail="Product not found")