import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv(Path(__file__).with_name(".env"))

from auth import (
    create_access_token,
    hash_password,
    read_access_token,
    validate_token_configuration,
    verify_password,
)
from database import (
    ForeignKeyViolation,
    UniqueViolation,
    database_connection,
    initialize_database,
)
from schemas import (
    ChatMessageCreate,
    LoginData,
    OrderData,
    OrderStatusData,
    ProductData,
    RegisterData,
)
from websocket_manager import manager as websocket_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shopzone_api")

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:4173,http://127.0.0.1:4173,"
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    validate_token_configuration()
    initialize_database()
    app.state.database_ready = True
    yield


app = FastAPI(title="Day 17 ShopZone E-Commerce API", lifespan=lifespan)
bearer_scheme = HTTPBearer(auto_error=False)

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    origin = request.headers.get("origin") or "*"
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.exception_handler(Exception)
async def custom_general_exception_handler(request: Request, exc: Exception):
    logger.exception("Server error: %s", exc)
    err_msg = str(exc).lower()
    origin = request.headers.get("origin") or "*"
    if "unique" in err_msg or "already exists" in err_msg or "duplicate key" in err_msg:
        return JSONResponse(
            status_code=409,
            content={"detail": "Email already registered. Please sign in instead."},
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "The server encountered a problem. Please try again."},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )



def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Sign in to continue")
    try:
        email = read_access_token(credentials.credentials)
    except ValueError as error:
        raise HTTPException(
            status_code=401, detail="Invalid or expired access token"
        ) from error

    with database_connection() as connection:
        user = connection.execute(
            "SELECT id, name, email, role FROM users WHERE email = %s",
            (email,),
        ).fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    return dict(user)


def require_admin(
    user: dict[str, Any] = Depends(require_authenticated_user),
) -> dict[str, Any]:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Day 17 ShopZone E-Commerce Backend Running"}


@app.get("/products")
def get_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    search: str | None = Query(default=None),
) -> list[dict[str, object]]:
    with database_connection() as connection:
        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            rows = connection.execute(
                """
                SELECT id, name, price, category, image
                FROM products
                WHERE LOWER(name) LIKE %s OR LOWER(category) LIKE %s
                ORDER BY id
                LIMIT %s OFFSET %s
                """,
                (term, term, limit, skip),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, name, price, category, image
                FROM products
                ORDER BY id
                LIMIT %s OFFSET %s
                """,
                (limit, skip),
            ).fetchall()
    return [dict(row) for row in rows]


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict[str, object]:
    with database_connection() as connection:
        row = connection.execute(
            """
            SELECT id, name, price, category, image
            FROM products
            WHERE id = %s
            """,
            (product_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)


@app.post("/auth/register")
def register(data: RegisterData) -> dict[str, object]:
    email = data.email.strip().lower()
    name = data.name.strip()
    if not name or "@" not in email:
        raise HTTPException(
            status_code=422, detail="A valid name and email are required"
        )

    try:
        with database_connection() as connection:
            existing = connection.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,),
            ).fetchone()
            if existing is not None:
                raise HTTPException(
                    status_code=409,
                    detail="Email already registered. Please sign in instead.",
                )

            connection.execute(
                """
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, 'shopper')
                """,
                (name, email, hash_password(data.password)),
            )
    except HTTPException:
        raise
    except UniqueViolation as error:
        raise HTTPException(
            status_code=409,
            detail="Email already registered. Please sign in instead.",
        ) from error
    except Exception as error:
        if "unique" in str(error).lower() or "duplicate" in str(error).lower():
            raise HTTPException(
                status_code=409,
                detail="Email already registered. Please sign in instead.",
            ) from error
        raise

    return {"success": True, "message": "Registration successful"}


@app.post("/auth/login")
def login(data: LoginData) -> dict[str, object]:
    email = data.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    with database_connection() as connection:
        user = connection.execute(
            """
            SELECT id, name, email, password_hash, role
            FROM users
            WHERE email = %s
            """,
            (email,),
        ).fetchone()

    if user is None or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "success": True,
        "message": "Login successful",
        "token": create_access_token(user["email"]),
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        },
    }


@app.get("/auth/me")
def get_me(user: dict[str, Any] = Depends(require_authenticated_user)) -> dict[str, Any]:
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


def _clean_product(product: ProductData) -> tuple[str, float, str, str]:
    name = product.name.strip()
    category = product.category.strip()
    image = product.image.strip()
    if not name or not category or not image:
        raise HTTPException(status_code=422, detail="Product fields cannot be blank")
    return name, product.price, category, image


def _insert_product(product: ProductData) -> dict[str, object]:
    with database_connection() as connection:
        row = connection.execute(
            """
            INSERT INTO products (name, price, category, image)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, price, category, image
            """,
            _clean_product(product),
        ).fetchone()
    if row is None:
        raise RuntimeError("The database did not return the new product")
    return dict(row)


@app.post("/products", dependencies=[Depends(require_admin)])
def create_product(product: ProductData) -> dict[str, object]:
    return _insert_product(product)


@app.get("/admin/products", dependencies=[Depends(require_admin)])
def get_admin_products() -> list[dict[str, object]]:
    with database_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, price, category, image FROM products ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


@app.post("/admin/products", dependencies=[Depends(require_admin)])
def admin_create_product(product: ProductData) -> dict[str, object]:
    return _insert_product(product)


@app.put(
    "/admin/products/{product_id}",
    dependencies=[Depends(require_admin)],
)
def admin_update_product(
    product_id: int,
    product: ProductData,
) -> dict[str, object]:
    with database_connection() as connection:
        row = connection.execute(
            """
            UPDATE products
            SET name = %s, price = %s, category = %s, image = %s
            WHERE id = %s
            RETURNING id, name, price, category, image
            """,
            (*_clean_product(product), product_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)


@app.delete(
    "/admin/products/{product_id}",
    dependencies=[Depends(require_admin)],
)
def admin_delete_product(product_id: int) -> dict[str, object]:
    try:
        with database_connection() as connection:
            row = connection.execute(
                "DELETE FROM products WHERE id = %s RETURNING id",
                (product_id,),
            ).fetchone()
    except ForeignKeyViolation as error:
        raise HTTPException(
            status_code=409,
            detail="Product cannot be deleted because it is included in an order",
        ) from error
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True, "message": "Product deleted"}


def _order_items(
    connection: Any,
    order_ids: list[int],
) -> dict[int, list[dict[str, object]]]:
    if not order_ids:
        return {}
    rows = connection.execute(
        """
        SELECT item.order_id, item.id, item.product_id,
               COALESCE(item.product_name, product.name) AS name,
               item.quantity, item.unit_price
        FROM order_items AS item
        JOIN products AS product ON product.id = item.product_id
        WHERE item.order_id = ANY(%s)
        ORDER BY item.order_id, item.id
        """,
        (order_ids,),
    ).fetchall()
    result: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        item = dict(row)
        order_id = item.pop("order_id")
        result.setdefault(order_id, []).append(item)
    return result


def _attach_order_items(
    connection: Any,
    orders: list[dict[str, Any]],
) -> list[dict[str, object]]:
    order_ids = [order["id"] for order in orders]
    items_by_order = _order_items(connection, order_ids)
    return [
        {**dict(order), "items": items_by_order.get(order["id"], [])}
        for order in orders
    ]


@app.post("/orders")
async def create_order(
    order: OrderData,
    user: dict[str, Any] = Depends(require_authenticated_user),
) -> dict[str, object]:
    details = {
        field: getattr(order, field).strip()
        for field in (
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "payment_method",
        )
    }
    if any(not value for value in details.values()):
        raise HTTPException(
            status_code=422, detail="Order contact and delivery fields are required"
        )
    if "@" not in details["email"]:
        raise HTTPException(status_code=422, detail="A valid order email is required")

    product_ids = sorted({item.product_id for item in order.items})
    with database_connection() as connection:
        products = connection.execute(
            """
            SELECT id, name, price
            FROM products
            WHERE id = ANY(%s)
            ORDER BY id
            FOR SHARE
            """,
            (product_ids,),
        ).fetchall()
        product_map = {product["id"]: product for product in products}
        if len(product_map) != len(product_ids):
            raise HTTPException(
                status_code=404, detail="One or more products were not found"
            )

        total = sum(
            (product_map[item.product_id]["price"] * item.quantity for item in order.items),
            0.0,
        )
        order_row = connection.execute(
            """
            INSERT INTO orders (
                user_id, email, total, status, full_name, phone, address,
                city, state, pincode, payment_method
            )
            VALUES (%s, %s, %s, 'pending', %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, status, total, created_at
            """,
            (
                user["id"],
                details["email"].lower(),
                total,
                details["full_name"],
                details["phone"],
                details["address"],
                details["city"],
                details["state"],
                details["pincode"],
                details["payment_method"],
            ),
        ).fetchone()
        if order_row is None:
            raise RuntimeError("The database did not return the new order")
        order_id = order_row["id"]
        for item in order.items:
            connection.execute(
                """
                INSERT INTO order_items (
                    order_id, product_id, product_name, quantity, unit_price
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    order_id,
                    item.product_id,
                    product_map[item.product_id]["name"],
                    item.quantity,
                    product_map[item.product_id]["price"],
                ),
            )
        item_rows = _order_items(connection, [order_id])


    result_order = dict(order_row)
    result_order["items"] = item_rows.get(order_id, [])

    # Real-time WebSocket event broadcast
    order_event = {
        "order_id": order_id,
        "user_id": user["id"],
        "email": details["email"].lower(),
        "status": "pending",
        "total": total,
        "created_at": str(result_order.get("created_at", "")),
        "items": result_order["items"],
        "message": f"Order #{order_id} placed successfully.",
    }
    await websocket_manager.broadcast_order_update(order_event, details["email"].lower())

    # Notification event broadcast
    notification_data = {
        "id": f"notif-order-{order_id}-{int(time.time()*1000)}",
        "order_id": order_id,
        "title": "Order Confirmed",
        "message": f"Your order #{order_id} has been confirmed.",
        "type": "confirmed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "read": False,
    }
    await websocket_manager.broadcast_notification(notification_data, details["email"].lower())

    return {
        "success": True,
        "message": "Order placed successfully",
        "order": result_order,
    }


@app.get("/orders")
def get_order_history(
    user: dict[str, Any] = Depends(require_authenticated_user),
) -> list[dict[str, object]]:
    with database_connection() as connection:
        orders = connection.execute(
            """
            SELECT id, status, total, created_at
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC, id DESC
            """,
            (user["id"],),
        ).fetchall()
        return _attach_order_items(connection, orders)


@app.get("/admin/orders", dependencies=[Depends(require_admin)])
def get_admin_orders() -> list[dict[str, object]]:
    with database_connection() as connection:
        orders = connection.execute(
            """
            SELECT id, user_id, email, status, total, created_at, full_name,
                   phone, address, city, state, pincode, payment_method
            FROM orders
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
        return _attach_order_items(connection, orders)


@app.patch(
    "/admin/orders/{order_id}/status",
    dependencies=[Depends(require_admin)],
)
async def update_order_status(
    order_id: int,
    data: OrderStatusData,
) -> dict[str, object]:
    with database_connection() as connection:
        row = connection.execute(
            """
            UPDATE orders
            SET status = %s
            WHERE id = %s
            RETURNING id, status, total, email, user_id
            """,
            (data.status, order_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")

    order_info = dict(row)
    customer_email = order_info.get("email", "").lower()

    # Real-time WebSocket Order update broadcast
    order_event = {
        "order_id": order_id,
        "status": data.status,
        "email": customer_email,
        "total": order_info.get("total", 0.0),
        "user_id": order_info.get("user_id"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "message": f"Order #{order_id} status updated to {data.status}.",
    }
    await websocket_manager.broadcast_order_update(order_event, customer_email)

    # Real-time Notification broadcast
    notification_title_map = {
        "pending": "Order Confirmed",
        "processing": "Order Processing",
        "shipped": "Order Shipped",
        "delivered": "Order Delivered",
        "cancelled": "Order Cancelled",
    }
    title = notification_title_map.get(data.status, f"Order {data.status.capitalize()}")
    notification_data = {
        "id": f"notif-order-{order_id}-{data.status}-{int(time.time()*1000)}",
        "order_id": order_id,
        "title": title,
        "message": f"Your order #{order_id} status is now {data.status}.",
        "type": data.status,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "read": False,
    }
    await websocket_manager.broadcast_notification(notification_data, customer_email)

    return {
        "success": True,
        "message": "Order status updated",
        "order": {"id": order_id, "status": data.status},
    }


# ===================== CHAT REST APIS =====================


@app.get("/chat/messages")
def get_chat_messages(
    customer: str | None = Query(default=None),
    user: dict[str, Any] = Depends(require_authenticated_user),
) -> list[dict[str, Any]]:
    with database_connection() as connection:
        if user["role"] == "admin":
            if customer and customer.strip():
                c_email = customer.strip().lower()
                rows = connection.execute(
                    """
                    SELECT id, sender_email, sender_name, sender_role,
                           recipient_email, message, created_at
                    FROM chat_messages
                    WHERE (sender_email = %s)
                       OR (recipient_email = %s)
                    ORDER BY created_at ASC
                    LIMIT 200
                    """,
                    (c_email, c_email),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT id, sender_email, sender_name, sender_role,
                           recipient_email, message, created_at
                    FROM chat_messages
                    ORDER BY created_at ASC
                    LIMIT 200
                    """
                ).fetchall()
        else:
            u_email = user["email"].strip().lower()
            rows = connection.execute(
                """
                SELECT id, sender_email, sender_name, sender_role,
                       recipient_email, message, created_at
                FROM chat_messages
                WHERE sender_email = %s OR recipient_email = %s
                ORDER BY created_at ASC
                LIMIT 200
                """,
                (u_email, u_email),
            ).fetchall()

    return [
        {
            "id": row["id"],
            "sender_email": row["sender_email"],
            "sender_name": row["sender_name"],
            "sender_role": row["sender_role"],
            "recipient_email": row["recipient_email"],
            "text": row["message"],
            "created_at": str(row["created_at"]),
        }
        for row in rows
    ]


@app.post("/chat/messages")
async def send_chat_message_rest(
    data: ChatMessageCreate,
    user: dict[str, Any] = Depends(require_authenticated_user),
) -> dict[str, Any]:
    text = data.message.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Message cannot be empty")

    recipient = data.recipient_email.strip().lower()
    if user["role"] != "admin":
        recipient = "admin"

    with database_connection() as connection:
        row = connection.execute(
            """
            INSERT INTO chat_messages (
                sender_email, sender_name, sender_role, recipient_email, message
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, created_at
            """,
            (user["email"], user["name"], user["role"], recipient, text),
        ).fetchone()

    msg_id = row["id"] if row else 0
    created_at = str(row["created_at"]) if row else datetime.now(timezone.utc).isoformat()
    chat_data = {
        "id": msg_id,
        "sender_email": user["email"],
        "sender_name": user["name"],
        "sender_role": user["role"],
        "recipient_email": recipient,
        "text": text,
        "created_at": created_at,
    }
    await websocket_manager.broadcast_chat_message(chat_data)
    return {"success": True, "message": "Message sent", "data": chat_data}


# ===================== WEBSOCKET ENDPOINT =====================


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str | None = Query(default=None),
) -> None:
    user_info = {
        "id": 0,
        "name": "Guest",
        "email": "guest",
        "role": "guest",
    }
    if token:
        try:
            email = read_access_token(token)
            with database_connection() as conn:
                db_user = conn.execute(
                    "SELECT id, name, email, role FROM users WHERE email = %s",
                    (email,),
                ).fetchone()
            if db_user:
                user_info = dict(db_user)
        except Exception:
            pass

    await websocket_manager.connect(websocket, user_info)
    try:
        while True:

            raw_text = await websocket.receive_text()
            try:
                message = json.loads(raw_text)
            except Exception:
                continue

            msg_type = message.get("type", "").upper()

            if msg_type == "PING":
                await websocket.send_text(json.dumps({"type": "PONG", "timestamp": int(time.time())}))

            elif msg_type == "AUTHENTICATE":
                auth_token = message.get("token")
                if auth_token:
                    try:
                        email = read_access_token(auth_token)
                        with database_connection() as conn:
                            db_user = conn.execute(
                                "SELECT id, name, email, role FROM users WHERE email = %s",
                                (email,),
                            ).fetchone()
                        if db_user:
                            user_info = dict(db_user)
                            websocket_manager.update_user(websocket, user_info)
                            await websocket.send_text(
                                json.dumps({
                                    "type": "AUTH_SUCCESS",
                                    "data": {"user": user_info},
                                })
                            )
                    except Exception as err:
                        await websocket.send_text(
                            json.dumps({
                                "type": "AUTH_ERROR",
                                "message": str(err),
                            })
                        )

            elif msg_type == "CHAT_MESSAGE":
                text = (message.get("text") or message.get("message") or "").strip()
                if not text:
                    continue

                recipient = message.get("recipient_email", "admin").strip().lower()
                if user_info.get("role") != "admin":
                    recipient = "admin"

                sender_email = user_info.get("email", "guest")
                sender_name = user_info.get("name", "Guest")
                sender_role = user_info.get("role", "guest")

                with database_connection() as conn:
                    row = conn.execute(
                        """
                        INSERT INTO chat_messages (
                            sender_email, sender_name, sender_role, recipient_email, message
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id, created_at
                        """,
                        (sender_email, sender_name, sender_role, recipient, text),
                    ).fetchone()

                msg_id = row["id"] if row else 0
                created_at = (
                    str(row["created_at"])
                    if row
                    else datetime.now(timezone.utc).isoformat()
                )
                chat_data = {
                    "id": msg_id,
                    "sender_email": sender_email,
                    "sender_name": sender_name,
                    "sender_role": sender_role,
                    "recipient_email": recipient,
                    "text": text,
                    "created_at": created_at,
                }
                await websocket_manager.broadcast_chat_message(chat_data)

    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as error:
        logger.debug("WebSocket connection error: %s", error)
        await websocket_manager.disconnect(websocket)
