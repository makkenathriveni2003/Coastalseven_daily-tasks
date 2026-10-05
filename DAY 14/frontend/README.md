# Daylight shop

A responsive React storefront built with Vite, React Router, Zustand, and TanStack Query.

## Run locally

Install and start the FastAPI server from the backend directory:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Create the virtual environment first if needed with
`py -m venv .venv`.

In another terminal, start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` to the backend base URL when it is not running at
`http://127.0.0.1:8000`.

## State and performance

- Zustand owns the cart and persists it in browser local storage; the auth store
  provides a demo sign-in state and is intentionally not persisted.
- TanStack Query caches product pages and requests additional pages as the
  product list is scrolled.
- Product and cart routes are lazy-loaded. Product cards are memoized and
  product images are lazy-loaded with responsive image parameters.
- `npm run lint` and `npm run build` validate the frontend.
