from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_admin_user
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.utils.redis_cache import delete_cache, get_cache, set_cache

router = APIRouter(prefix="/products", tags=["Products"])


def product_to_cache_dict(product: Product):
    return {key: value for key, value in product.__dict__.items() if not key.startswith("_")}


@router.get("/", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    cache_key = "products:list"
    cached = get_cache(cache_key)
    if cached is not None:
        return cached

    products = db.query(Product).all()
    serialized = [product_to_cache_dict(product) for product in products]
    set_cache(cache_key, serialized)
    return products


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    cache_key = f"product:{product_id}"
    cached = get_cache(cache_key)
    if cached is not None:
        return cached

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    set_cache(cache_key, product_to_cache_dict(product))
    return product


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_admin_user),
):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    delete_cache("products:list")
    return db_product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(get_admin_user),
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.model_dump().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    delete_cache("products:list")
    delete_cache(f"product:{product_id}")
    return db_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_admin_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    delete_cache("products:list")
    delete_cache(f"product:{product_id}")
    return {"message": "Product deleted successfully"}
