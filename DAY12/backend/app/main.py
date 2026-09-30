from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Day 12 E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

products = [
    {"id": 1, "name": "Laptop", "price": 50000},
    {"id": 2, "name": "Mobile", "price": 25000},
    {"id": 3, "name": "Headphones", "price": 3000},
]


@app.get("/")
def home():
    return {"message": "Day 12 E-Commerce API is running"}


@app.get("/products")
def get_products():
    return products