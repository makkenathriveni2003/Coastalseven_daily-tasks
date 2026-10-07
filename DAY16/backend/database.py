import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

try:
    import psycopg
    from psycopg.errors import (
        ForeignKeyViolation as BaseForeignKeyViolation,
        UniqueViolation as BaseUniqueViolation,
    )
    from psycopg.rows import dict_row

    HAS_PSYCOPG = True
except ImportError:
    HAS_PSYCOPG = False
    BaseForeignKeyViolation = Exception
    BaseUniqueViolation = Exception


class UniqueViolation(BaseUniqueViolation):
    """Raised when a unique constraint is violated."""
    pass


class ForeignKeyViolation(BaseForeignKeyViolation):
    """Raised when a foreign key constraint is violated."""
    pass


_ENGINE: str | None = None
_SQLITE_PATH = Path(__file__).resolve().parent / "ecommerce.db"


def _detect_engine() -> str:
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    forced = os.getenv("DATABASE_ENGINE", "").strip().lower()
    if forced in ("sqlite", "sqlite3"):
        _ENGINE = "sqlite"
        return _ENGINE
    if forced in ("postgres", "postgresql", "psql"):
        _ENGINE = "postgres"
        return _ENGINE
    if forced:
        raise ValueError(
            "DATABASE_ENGINE must be set to 'postgres' or 'sqlite'."
        )

    # Check if PostgreSQL connection can be established within 1 second
    if HAS_PSYCOPG:
        try:
            with psycopg.connect(
                host=os.getenv("PGHOST", "localhost"),
                port=int(os.getenv("PGPORT", "5432")),
                dbname=os.getenv("PGDATABASE") or "sqlight",
                user=os.getenv("PGUSER") or "Thriveni",
                password=os.getenv("PGPASSWORD") or None,
                connect_timeout=1,
            ):
                _ENGINE = "postgres"
                return _ENGINE
        except psycopg.Error as error:
            raise RuntimeError(
                "PostgreSQL is unavailable. Start PostgreSQL or explicitly set "
                "DATABASE_ENGINE=sqlite for local development."
            ) from error

    raise RuntimeError(
        "PostgreSQL support is not installed. Install backend requirements "
        "or explicitly set DATABASE_ENGINE=sqlite for local development."
    )


def _connect_pg() -> Any:
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE") or "sqlight",
        user=os.getenv("PGUSER") or "Thriveni",
        password=os.getenv("PGPASSWORD") or None,
        connect_timeout=5,
        row_factory=dict_row,
    )


class SQLiteCursorWrapper:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    def fetchone(self) -> dict[str, Any] | None:
        row = self._cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self._cursor.fetchall()]


class SQLiteConnectionWrapper:
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def _prepare_sql_and_params(
        self, sql: str, params: Any = ()
    ) -> tuple[str, list[Any]]:
        cleaned = re.sub(r"\bFOR\s+SHARE\b", "", sql, flags=re.IGNORECASE)
        new_params: list[Any] = []
        if params:
            for p in params:
                if isinstance(p, (list, tuple, set)):
                    p_list = list(p)
                    if not p_list:
                        placeholders = "NULL"
                    else:
                        placeholders = ", ".join(["?"] * len(p_list))
                    cleaned = re.sub(
                        r"=\s*ANY\s*\(\s*%s\s*\)",
                        f"IN ({placeholders})",
                        cleaned,
                        count=1,
                        flags=re.IGNORECASE,
                    )
                    new_params.extend(p_list)
                else:
                    new_params.append(p)
        cleaned = cleaned.replace("%s", "?")
        return cleaned, new_params

    def execute(self, sql: str, params: Any = ()) -> SQLiteCursorWrapper:
        cleaned_sql, new_params = self._prepare_sql_and_params(sql, params)
        try:
            cur = self._conn.cursor()
            cur.execute(cleaned_sql, new_params)
            return SQLiteCursorWrapper(cur)
        except sqlite3.IntegrityError as error:
            msg = str(error).lower()
            if "unique" in msg:
                raise UniqueViolation(str(error)) from error
            if "foreign key" in msg:
                raise ForeignKeyViolation(str(error)) from error
            raise

    def executemany(self, sql: str, params_seq: Any) -> SQLiteCursorWrapper:
        cleaned_sql = sql.replace("%s", "?")
        try:
            cur = self._conn.cursor()
            cur.executemany(cleaned_sql, params_seq)
            return SQLiteCursorWrapper(cur)
        except sqlite3.IntegrityError as error:
            msg = str(error).lower()
            if "unique" in msg:
                raise UniqueViolation(str(error)) from error
            if "foreign key" in msg:
                raise ForeignKeyViolation(str(error)) from error
            raise

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


@contextmanager
def database_connection() -> Generator[Any, None, None]:
    engine = _detect_engine()
    if engine == "postgres":
        with _connect_pg() as connection:
            yield connection
    else:
        conn = sqlite3.connect(str(_SQLITE_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        wrapper = SQLiteConnectionWrapper(conn)
        try:
            yield wrapper
            wrapper.commit()
        except Exception:
            wrapper.rollback()
            raise
        finally:
            wrapper.close()


DEFAULT_CATALOG = [
    {"name": "Laptop", "price": 55000.0, "category": "Electronics", "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500"},
    {"name": "Mobile", "price": 25000.0, "category": "Electronics", "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500"},
    {"name": "Headphones", "price": 3000.0, "category": "Accessories", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"},
    {"name": "Smart Watch", "price": 5000.0, "category": "Accessories", "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"},
    {"name": "Women's Dress", "price": 1999.0, "category": "Fashion", "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500"},
    {"name": "Men's Casual Shirt", "price": 1299.0, "category": "Fashion", "image": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500"},
    {"name": "Denim Jeans", "price": 1799.0, "category": "Fashion", "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500"},
    {"name": "Women's Kurti", "price": 1499.0, "category": "Fashion", "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500"},
    {"name": "Gold Necklace", "price": 2499.0, "category": "Jewellery", "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500"},
    {"name": "Elegant Earrings", "price": 999.0, "category": "Jewellery", "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500"},
    {"name": "Bracelet", "price": 799.0, "category": "Jewellery", "image": "https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=500"},
    {"name": "Fashion Ring", "price": 699.0, "category": "Jewellery", "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500"},
    {"name": "Running Shoes", "price": 2499.0, "category": "Shoes", "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"},
    {"name": "Women's Sneakers", "price": 2199.0, "category": "Shoes", "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500"},
    {"name": "Women's Handbag", "price": 1899.0, "category": "Bags", "image": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500"},
    {"name": "Travel Backpack", "price": 1599.0, "category": "Bags", "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500"},
]


def _seed_initial_data(connection: Any) -> None:
    # Seed products if empty
    product_rows = connection.execute("SELECT COUNT(*) AS count FROM products").fetchone()
    count = product_rows["count"] if product_rows else 0
    if count == 0:
        for p in DEFAULT_CATALOG:
            connection.execute(
                """
                INSERT INTO products (name, price, category, image)
                VALUES (%s, %s, %s, %s)
                """,
                (p["name"], p["price"], p["category"], p["image"]),
            )

def initialize_database() -> None:
    engine = _detect_engine()
    if engine == "postgres":
        with database_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL CHECK (price >= 0),
                    category TEXT NOT NULL,
                    image TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_attribute
                        WHERE attrelid = 'products'::regclass
                          AND attname = 'id'
                          AND attidentity IN ('a', 'd')
                    ) THEN
                        ALTER TABLE products
                        ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY;
                    END IF;
                END
                $$
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'shopper',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT"
            )
            connection.execute(
                "UPDATE users SET role = 'shopper' WHERE role IS NULL"
            )
            connection.execute(
                "ALTER TABLE users ALTER COLUMN role SET DEFAULT 'shopper'"
            )
            connection.execute(
                "ALTER TABLE users ALTER COLUMN role SET NOT NULL"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    email TEXT NOT NULL,
                    total REAL NOT NULL CHECK (total >= 0),
                    status TEXT NOT NULL DEFAULT 'pending',
                    user_id INTEGER REFERENCES users(id),
                    full_name TEXT,
                    phone TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    pincode TEXT,
                    payment_method TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                ALTER TABLE orders
                    ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending',
                    ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id),
                    ADD COLUMN IF NOT EXISTS full_name TEXT,
                    ADD COLUMN IF NOT EXISTS phone TEXT,
                    ADD COLUMN IF NOT EXISTS address TEXT,
                    ADD COLUMN IF NOT EXISTS city TEXT,
                    ADD COLUMN IF NOT EXISTS state TEXT,
                    ADD COLUMN IF NOT EXISTS pincode TEXT,
                    ADD COLUMN IF NOT EXISTS payment_method TEXT,
                    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                """
            )
            connection.execute(
                "UPDATE orders SET status = 'pending' WHERE status IS NULL"
            )
            connection.execute(
                "ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'pending'"
            )
            connection.execute(
                "ALTER TABLE orders ALTER COLUMN status SET NOT NULL"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    order_id INTEGER NOT NULL REFERENCES orders(id),
                    product_id INTEGER NOT NULL REFERENCES products(id),
                    product_name TEXT,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    unit_price REAL NOT NULL CHECK (unit_price >= 0)
                )
                """
            )
            connection.execute(
                "ALTER TABLE order_items ADD COLUMN IF NOT EXISTS product_name TEXT"
            )
            connection.execute(
                """
                UPDATE order_items AS item
                SET product_name = product.name
                FROM products AS product
                WHERE item.product_id = product.id
                  AND item.product_name IS NULL
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS orders_user_created_idx ON orders (user_id, created_at DESC)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS order_items_order_idx ON order_items (order_id, id)"
            )
            _seed_initial_data(connection)
    else:
        with database_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL CHECK (price >= 0),
                    category TEXT NOT NULL,
                    image TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'shopper',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    total REAL NOT NULL CHECK (total >= 0),
                    status TEXT NOT NULL DEFAULT 'pending',
                    user_id INTEGER REFERENCES users(id),
                    full_name TEXT,
                    phone TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    pincode TEXT,
                    payment_method TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL REFERENCES orders(id),
                    product_id INTEGER NOT NULL REFERENCES products(id),
                    product_name TEXT,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    unit_price REAL NOT NULL CHECK (unit_price >= 0)
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS orders_user_created_idx ON orders (user_id, created_at DESC)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS order_items_order_idx ON order_items (order_id, id)"
            )
            _seed_initial_data(connection)
