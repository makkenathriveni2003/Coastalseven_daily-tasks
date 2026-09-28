from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None


class ProductUpdate(ProductCreate):
    pass


class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
