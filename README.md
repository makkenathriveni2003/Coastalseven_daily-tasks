# Secure Product API - Day 6

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## Main endpoints

- POST /register
- POST /login
- GET /me
- POST /refresh
- GET /products
- POST /products (admin only)
- PUT /products/{product_id} (admin only)

## Important
This is a learning project. Before production use, restrict CORS, use a strong secret key, use HTTPS, and do not allow public registration to choose the admin role.
