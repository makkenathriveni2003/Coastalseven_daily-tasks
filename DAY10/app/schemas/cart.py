from typing import List

from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0)


class CartItemResponse(BaseModel):
    product_id: int
    quantity: int


class CartResponse(BaseModel):
    items: List[CartItemResponse]
