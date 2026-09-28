import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_admin_user, get_current_user
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.redis_client import safe_delete, safe_get
from app.tasks.email_tasks import send_order_confirmation_email
from app.schemas.order import OrderOut, OrderStatusUpdate
from typing import List
from app.websocket_manager import manager

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_cart_key(user_id: int) -> str:
    return f"cart:{user_id}"

@router.get("/", response_model=List[OrderOut])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.id.desc())
        .all()
    )
    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "total_price": order.total_price,
            "status": order.status,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price,
                }
                for item in db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            ],
        }
        for order in orders
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_key = get_cart_key(current_user.id)
    cart_data = safe_get(cart_key)
    if not cart_data:
        raise HTTPException(status_code=400, detail="Cart is empty")

    import json

    cart_items = json.loads(cart_data)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_items = []
    total_price = 0.0

    for item in cart_items:
        product_id = item["product_id"]
        quantity = item["quantity"]
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        if product.stock < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.name}",
            )

        product.stock -= quantity
        total_price += product.price * quantity
        order_items.append(
            {
                "product_id": product_id,
                "quantity": quantity,
                "price": product.price,
            }
        )

    order = Order(user_id=current_user.id, total_price=total_price, status="pending")
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"],
        )
        db.add(order_item)

    db.commit()

    safe_delete(cart_key)
    try:
        send_order_confirmation_email.delay(current_user.email, order.id)
    except Exception:
        pass

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "status": order.status,
        "items": order_items,
    }


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = update.status
    db.commit()
    await manager.broadcast(
        f"user:{order.user_id}",
        json.dumps({"type": "order_status", "order_id": order.id, "status": order.status}),
    )
    return {"id": order.id, "status": order.status}
