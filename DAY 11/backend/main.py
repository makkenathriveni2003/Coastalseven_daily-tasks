import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date as date_type, datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Literal

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pwdlib import PasswordHash


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "daybook.sqlite3")))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("Set JWT_SECRET_KEY before starting the API")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


def connect_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def database_connection():
    connection = connect_database()
    try:
        yield connection
    finally:
        connection.close()


def initialize_database():
    with database_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                time TEXT,
                priority TEXT NOT NULL CHECK (priority IN ('low', 'normal', 'high')),
                date TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_tasks_user_date ON tasks(user_id, date);
            """
        )
        connection.commit()


initialize_database()

app = FastAPI(title="Daybook API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized.count("@") != 1 or "." not in normalized.rsplit("@", 1)[1]:
            raise ValueError("Enter a valid email address")
        return normalized


class Registration(Credentials):
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    time: str | None = None
    priority: Literal["low", "normal", "high"] = "normal"
    date: date_type | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Task title cannot be blank")
        return value


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=100)
    time: str | None = None
    priority: Literal["low", "normal", "high"] | None = None
    date: date_type | None = None
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Task title cannot be blank")
        return value


class TaskResponse(BaseModel):
    id: str
    title: str
    time: str | None
    priority: Literal["low", "normal", "high"]
    date: date_type
    completed: bool


def make_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def get_database():
    with database_connection() as connection:
        yield connection


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
):
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized from None
    user = connection.execute(
        "SELECT id, email FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    if user is None:
        raise unauthorized
    return dict(user)


def serialize_task(row: sqlite3.Row) -> dict:
    task = dict(row)
    task["completed"] = bool(task["completed"])
    return task


def get_owned_task(connection: sqlite3.Connection, task_id: str, user_id: int):
    task = connection.execute(
        "SELECT id, title, time, priority, date, completed FROM tasks "
        "WHERE id = ? AND user_id = ?",
        (task_id, user_id),
    ).fetchone()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=AuthResponse, status_code=201)
def register_account(
    account: Registration,
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
):
    created_at = datetime.now(timezone.utc).isoformat()
    try:
        cursor = connection.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (account.email, password_hash.hash(account.password), created_at),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists") from None
    user = {"id": cursor.lastrowid, "email": account.email}
    return {"access_token": make_access_token(user["id"]), "user": user}


@app.post("/api/auth/login", response_model=AuthResponse)
def login(
    account: Credentials,
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
):
    user = connection.execute(
        "SELECT id, email, password_hash FROM users WHERE email = ? COLLATE NOCASE",
        (account.email,),
    ).fetchone()
    if user is None or not password_hash.verify(account.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    public_user = {"id": user["id"], "email": user["email"]}
    return {"access_token": make_access_token(user["id"]), "user": public_user}


@app.get("/api/auth/me", response_model=UserResponse)
def read_current_user(user: Annotated[dict, Depends(get_current_user)]):
    return user


@app.get("/api/tasks", response_model=list[TaskResponse])
def list_tasks(
    user: Annotated[dict, Depends(get_current_user)],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
):
    rows = connection.execute(
        "SELECT id, title, time, priority, date, completed FROM tasks "
        "WHERE user_id = ? ORDER BY date, COALESCE(time, '99:99'), created_at DESC",
        (user["id"],),
    ).fetchall()
    return [serialize_task(row) for row in rows]


@app.post("/api/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    user: Annotated[dict, Depends(get_current_user)],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
):
    task_id = str(uuid.uuid4())
    task_date = (task.date or date_type.today()).isoformat()
    connection.execute(
        "INSERT INTO tasks (id, user_id, title, time, priority, date, completed, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, 0, ?)",
        (
            task_id,
            user["id"],
            task.title,
            task.time,
            task.priority,
            task_date,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    connection.commit()
    return serialize_task(get_owned_task(connection, task_id, user["id"]))


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def read_task(
    task_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
):
    return serialize_task(get_owned_task(connection, task_id, user["id"]))


@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    update: TaskUpdate,
    user: Annotated[dict, Depends(get_current_user)],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
):
    task = get_owned_task(connection, task_id, user["id"])
    changes = update.model_dump(exclude_unset=True)
    if any(changes.get(key) is None for key in ("title", "priority", "date", "completed") if key in changes):
        raise HTTPException(status_code=422, detail="A required task field cannot be null")
    if not changes:
        return serialize_task(task)
    for key, value in changes.items():
        changes[key] = value.isoformat() if isinstance(value, date_type) else value
    assignments = ", ".join(f"{key} = ?" for key in changes)
    connection.execute(
        f"UPDATE tasks SET {assignments} WHERE id = ? AND user_id = ?",
        (*changes.values(), task_id, user["id"]),
    )
    connection.commit()
    return serialize_task(get_owned_task(connection, task_id, user["id"]))


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
):
    get_owned_task(connection, task_id, user["id"])
    connection.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user["id"])
    )
    connection.commit()
