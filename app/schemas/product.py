from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)

class ProductResponse(ProductCreate):
    id: int
    model_config = {"from_attributes": True}
