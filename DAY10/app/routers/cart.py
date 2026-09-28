import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.product import Product
from app.models.user import User
from app.redis_client import safe_delete, safe_get, safe_set
from app.schemas.cart import CartItemRequest, CartResponse

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_cart_key(user_id: int) -> str:
    return f"cart:{user_id}"


def get_cart_items(user_id: int):
    raw_data = safe_get(get_cart_key(user_id))
    if not raw_data:
        return []
    try:
        items = json.loads(raw_data)
        return items if isinstance(items, list) else []
    except (TypeError, ValueError):
        return []


def save_cart_items(user_id: int, cart_items):
    safe_set(get_cart_key(user_id), json.dumps(cart_items))


@router.get("/", response_model=CartResponse)
def read_cart(current_user: User = Depends(get_current_user)):
    return {"items": get_cart_items(current_user.id)}


@router.post("/add", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item: CartItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_items = get_cart_items(current_user.id)
    existing_item = next(
        (cart for cart in cart_items if cart.get("product_id") == item.product_id),
        None,
    )

    if existing_item:
        existing_item["quantity"] += item.quantity
    else:
        cart_items.append({"product_id": item.product_id, "quantity": item.quantity})

    save_cart_items(current_user.id, cart_items)
    return {"items": cart_items}


@router.put("/update", response_model=CartResponse)
def update_cart_item(
    item: CartItemRequest,
    current_user: User = Depends(get_current_user),
):
    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    cart_items = get_cart_items(current_user.id)
    found = False
    for cart_item in cart_items:
        if cart_item.get("product_id") == item.product_id:
            cart_item["quantity"] = item.quantity
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    save_cart_items(current_user.id, cart_items)
    return {"items": cart_items}


@router.delete("/remove/{product_id}", response_model=CartResponse)
def remove_from_cart(product_id: int, current_user: User = Depends(get_current_user)):
    cart_items = get_cart_items(current_user.id)
    updated_items = [item for item in cart_items if item.get("product_id") != product_id]
    if len(updated_items) == len(cart_items):
        raise HTTPException(status_code=404, detail="Item not found in cart")

    save_cart_items(current_user.id, updated_items)
    return {"items": updated_items}


@router.delete("/clear", response_model=CartResponse)
def clear_cart(current_user: User = Depends(get_current_user)):
    safe_delete(get_cart_key(current_user.id))
    return {"items": []}
