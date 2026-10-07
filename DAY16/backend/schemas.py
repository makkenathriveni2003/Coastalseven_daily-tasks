from typing import Literal

from pydantic import BaseModel, Field


class LoginData(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class RegisterData(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class OrderItem(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1)


class OrderData(BaseModel):
    items: list[OrderItem] = Field(min_length=1)
    full_name: str = Field(min_length=1, max_length=150)
    email: str = Field(min_length=3, max_length=254)
    phone: str = Field(min_length=1, max_length=40)
    address: str = Field(min_length=1, max_length=500)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    pincode: str = Field(min_length=1, max_length=20)
    payment_method: Literal["cash_on_delivery", "card", "upi"]


class ProductData(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0, allow_inf_nan=False)
    category: str = Field(min_length=1, max_length=100)
    image: str = Field(min_length=1, max_length=2048)


class OrderStatusData(BaseModel):
    status: Literal["pending", "processing", "shipped", "delivered", "cancelled"]
