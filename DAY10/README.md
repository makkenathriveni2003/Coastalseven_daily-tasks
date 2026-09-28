# Day 10 Ecommerce API

A FastAPI-based ecommerce backend with authentication, product management, cart, orders, image upload, and websocket support.

## Features

- User registration and login
- JWT-based authentication
- Admin-only product management
- Shopping cart stored with Redis-compatible fallback
- Order creation with stock validation
- Image upload and resizing
- WebSocket order notifications
- SQLite default database setup for local development

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy
- Pydantic v2
- SQLite
- Redis (with graceful fallback in local/test mode)
- Celery (background task support with graceful fallback)
- Pytest

## Project Structure

```text
app/
  __init__.py
  celery_app.py
  config.py
  database.py
  dependencies.py
  main.py
  redis_client.py
  websocket_manager.py
  models/
  routers/
  schemas/
  services/
  tasks/
  tests/
  utils/
uploads/
requirements.txt
README.md
```

## Quick Start

1. Open the project folder:

```powershell
cd "c:\Users\Dell\Downloads\day10"
```

2. Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

4. Run the test suite:

```powershell
python -m pytest -q
```

5. Start the API server:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

6. Open the API documentation:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

## API Overview

### Authentication

- POST /auth/register
- POST /auth/login
- GET /auth/me

### Products

- GET /products/
- GET /products/{product_id}
- POST /products/
- PUT /products/{product_id}
- DELETE /products/{product_id}

### Cart

- GET /cart/
- POST /cart/add
- PUT /cart/update
- DELETE /cart/remove/{product_id}
- DELETE /cart/clear

### Orders

- POST /orders/

### Upload

- POST /upload/

### WebSocket

- WS /ws

## Notes

- The app uses SQLite by default for local development.
- Redis and Celery are supported, but the project includes safe fallback behavior when those services are unavailable during local testing.
- Uploaded images are resized and saved in the `uploads/` directory.

## Verification

The current project state has been verified with:

```powershell
python -m pytest -q
```

and the test suite passed successfully.

## Production Container

The project includes a Docker Compose baseline with PostgreSQL, Redis, persistent uploads, and a non-reload Uvicorn process.

1. Copy `.env.example` to `.env` and replace the secret values.
2. Start the services:

```powershell
docker compose up --build -d
```

3. Open the storefront at http://127.0.0.1:8000/store/ or API docs at http://127.0.0.1:8000/docs.

Stop the services with:

```powershell
docker compose down
```

Do not use the development SQLite defaults or the fallback services for a public deployment. Set a strong `SECRET_KEY`, protect PostgreSQL and Redis, and place the app behind HTTPS.
