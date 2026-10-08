from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv(Path(__file__).resolve().parent / ".env")

def get_database_url() -> str:
    engine_type = os.getenv("DATABASE_ENGINE", "postgres").strip().lower()
    if engine_type in ("sqlite", "sqlite3"):
        db_path = Path(__file__).resolve().parent / "ecommerce.db"
        return f"sqlite:///{db_path}"
    
    user = os.getenv("PGUSER", "Thriveni")
    password = os.getenv("PGPASSWORD", "")
    host = os.getenv("PGHOST", "127.0.0.1")
    port = os.getenv("PGPORT", "5432")
    dbname = os.getenv("PGDATABASE", "sqlight")
    
    if password:
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"
    return f"postgresql+psycopg://{user}@{host}:{port}/{dbname}"

DATABASE_URL = get_database_url()

# PostgreSQL vs SQLite engine args
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
