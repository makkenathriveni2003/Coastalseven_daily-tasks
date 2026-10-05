from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Day 13 E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

products = [
    # ELECTRONICS
    {
        "id": 1,
        "name": "Laptop",
        "price": 50000,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853"
    },
    {
        "id": 2,
        "name": "Mobile",
        "price": 25000,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"
    },
    {
        "id": 3,
        "name": "Headphones",
        "price": 3000,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"
    },
    {
        "id": 4,
        "name": "Smart Watch",
        "price": 4500,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30"
    },
    {
        "id": 5,
        "name": "Camera",
        "price": 35000,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32"
    },

    # FASHION
    {
        "id": 6,
        "name": "Women's Dress",
        "price": 1999,
        "category": "Fashion",
        "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8"
    },
    {
        "id": 7,
        "name": "Men's Casual Shirt",
        "price": 1299,
        "category": "Fashion",
        "image": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf"
    },
    {
        "id": 8,
        "name": "Denim Jeans",
        "price": 1799,
        "category": "Fashion",
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d"
    },
    {
        "id": 9,
        "name": "Women's Kurti",
        "price": 1499,
        "category": "Fashion",
        "image": "https://images.unsplash.com/photo-1583391733956-6c78276477e2"
    },

    # JEWELLERY
    {
        "id": 10,
        "name": "Gold Necklace",
        "price": 2499,
        "category": "Jewellery",
        "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f"
    },
    {
        "id": 11,
        "name": "Elegant Earrings",
        "price": 999,
        "category": "Jewellery",
        "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908"
    },
    {
        "id": 12,
        "name": "Fashion Bracelet",
        "price": 799,
        "category": "Jewellery",
        "image": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0"
    },
    {
        "id": 13,
        "name": "Fashion Ring",
        "price": 699,
        "category": "Jewellery",
        "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e"
    },

    # SHOES
    {
        "id": 14,
        "name": "Running Shoes",
        "price": 2499,
        "category": "Shoes",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff"
    },
    {
        "id": 15,
        "name": "Women's Sneakers",
        "price": 2199,
        "category": "Shoes",
        "image": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2"
    },

    # BAGS
    {
        "id": 16,
        "name": "Women's Handbag",
        "price": 1899,
        "category": "Bags",
        "image": "https://images.unsplash.com/photo-1584917865442-de89df76afd3"
    },
    {
        "id": 17,
        "name": "Travel Backpack",
        "price": 1599,
        "category": "Bags",
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62"
    },
]

users = []


class LoginData(BaseModel):
    email: str
    password: str


class RegisterData(BaseModel):
    name: str
    email: str
    password: str


class OrderItem(BaseModel):
    product_id: int
    quantity: int


class OrderData(BaseModel):
    email: str
    items: List[OrderItem]
    total: float


@app.get("/")
def home():
    return {"message": "Day 13 E-Commerce Backend Running"}


@app.get("/products")
def get_products():
    return products


@app.post("/auth/register")
def register(data: RegisterData):
    if any(u["email"] == data.email for u in users):
        return {
            "success": False,
            "message": "Email already registered"
        }

    users.append({
        "name": data.name,
        "email": data.email,
        "password": data.password
    })

    return {
        "success": True,
        "message": "Registration successful"
    }


@app.post("/auth/login")
def login(data: LoginData):
    user = next(
        (
            u for u in users
            if u["email"] == data.email
            and u["password"] == data.password
        ),
        None
    )

    if not user:
        return {
            "success": False,
            "message": "Invalid email or password"
        }

    return {
        "success": True,
        "message": "Login successful",
        "token": "day13-demo-token",
        "user": {
            "name": user["name"],
            "email": user["email"]
        }
    }


@app.post("/orders")
def create_order(order: OrderData):
    return {
        "success": True,
        "message": "Order placed successfully",
        "order": order
    }