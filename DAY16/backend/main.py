import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
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
    LoginData,
    OrderData,
    OrderStatusData,
    ProductData,
    RegisterData,
)


allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:4173,http://127.0.0.1:4173",
    ).split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    validate_token_configuration()
    initialize_database()
    app.state.database_ready = True
    yield


app = FastAPI(title="Day 16 E-Commerce API", lifespan=lifespan)
bearer_scheme = HTTPBearer(auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Day 16 E-Commerce Backend Running"}


@app.get("/products")
def get_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
) -> list[dict[str, object]]:
    with database_connection() as connection:
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


def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Sign in to continue")
    try:
        email = read_access_token(credentials.credentials)
    except ValueError as error:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from error

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


@app.post("/auth/register")
def register(data: RegisterData) -> dict[str, object]:
    email = data.email.strip().lower()
    name = data.name.strip()
    if not name or "@" not in email:
        raise HTTPException(status_code=422, detail="A valid name and email are required")

    try:
        with database_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, 'shopper')
                """,
                (name, email, hash_password(data.password)),
            )
    except UniqueViolation as error:
        raise HTTPException(status_code=409, detail="Email already registered") from error

    return {"success": True, "message": "Registration successful"}


@app.post("/auth/login")
def login(data: LoginData) -> dict[str, object]:
    email = data.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    with database_connection() as connection:
        user = connection.execute(
            """
            SELECT name, email, password_hash, role
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
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        },
    }


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


@app.post("/orders")
def create_order(
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
        raise HTTPException(status_code=422, detail="Order contact and delivery fields are required")
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
            raise HTTPException(status_code=404, detail="One or more products were not found")

        total = sum(
            (product_map[item.product_id]["price"] * item.quantity for item in order.items),
            0,
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
        connection.executemany(
            """
            INSERT INTO order_items (
                order_id, product_id, product_name, quantity, unit_price
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            [
                (
                    order_id,
                    item.product_id,
                    product_map[item.product_id]["name"],
                    item.quantity,
                    product_map[item.product_id]["price"],
                )
                for item in order.items
            ],
        )
        item_rows = _order_items(connection, [order_id])

    result_order = dict(order_row)
    result_order["items"] = item_rows.get(order_id, [])
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
def update_order_status(
    order_id: int,
    data: OrderStatusData,
) -> dict[str, object]:
    with database_connection() as connection:
        row = connection.execute(
            """
            UPDATE orders
            SET status = %s
            WHERE id = %s
            RETURNING id, status
            """,
            (data.status, order_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True, "message": "Order status updated", "order": dict(row)}


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
