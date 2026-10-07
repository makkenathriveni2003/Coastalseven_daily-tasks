# Day 16 — E-Commerce Frontend (Part 2)

Complete full-stack e-commerce application featuring global state management, authenticated checkout, customer order history, and an administrative dashboard connected end-to-end with the FastAPI backend.

## Project Structure

- `frontend/` — React 19 + TypeScript storefront:
  - **Zustand Cart Store** with localStorage persistence (`src/store/cartStore.ts`)
  - **Checkout Page** powered by `react-hook-form` and `zod` schema validation (`src/pages/Checkout.tsx`)
  - **Order History Page** displaying order status, timestamps, and item snapshots (`src/pages/OrderHistory.tsx`)
  - **Admin Dashboard** with product CRUD and order status management (`src/pages/AdminDashboard.tsx`)
  - **Dark / Light Mode** theme switcher with persistence (`src/App.tsx` & `src/index.css`)
  - **TanStack React Query** for server-state caching, synchronization, and mutations
  - **Automated Test Suite** of 48+ Vitest unit/component tests + MSW API mocks + Playwright E2E tests
- `backend/` — FastAPI REST API with dual PostgreSQL & SQLite support:
  - Authentication (JWT tokens, PBKDF2 password hashing, roles: `shopper`, `admin`)
  - Public & protected product endpoints (`GET /products`, `GET /products/{id}`, `POST /products`)
  - Admin product management (`GET/POST /admin/products`, `PUT/DELETE /admin/products/{id}`)
  - Orders & snapshots (`POST /orders`, `GET /orders`, `GET /admin/orders`, `PATCH /admin/orders/{id}/status`)
  - Seeded catalog (16 items) and default accounts (`admin@example.com` / `Admin@12345`, `shopper@example.com` / `Shopper@12345`)
- `.github/workflows/` — Automated CI workflow verifying typechecking, linting, tests, Playwright E2E, and production build.

## Running the Application

### 1. Backend (FastAPI)
```powershell
cd backend
# Uses virtual environment in day15/.venv or local .venv
& ..\..\day15\.venv\Scripts\uvicorn.exe main:app --host 127.0.0.1 --port 8000 --reload
```
API runs at `http://127.0.0.1:8000` (docs at `http://127.0.0.1:8000/docs`).

### 2. Frontend (React + Vite)
```powershell
cd frontend
npm run dev
```
Open `http://127.0.0.1:5174` (or `http://localhost:5173`).

### 3. Verification & Testing
```powershell
cd frontend
npm run typecheck    # TypeScript compiler check
npm run lint         # ESLint check
npm test             # Vitest test suite (48 tests passing)
npm run test:e2e     # Playwright E2E test suite
npm run build        # Production Vite build
```
