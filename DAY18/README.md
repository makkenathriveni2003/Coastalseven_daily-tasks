# Day 18 – ShopZone Advanced Backend & Performance Optimization

Complete full-stack implementation of the **Day 18 ShopZone E-Commerce platform** featuring asynchronous task queuing with Celery & Redis, dynamic PDF invoice generation with ReportLab, bulk product CSV import with validation, full-text & fuzzy search on PostgreSQL, Alembic database schema migrations, and optimized SQLAlchemy queries solving N+1 bottlenecks.

---

## 1. Day 18 Objectives & Architecture

1. **Asynchronous Background Processing (Celery + Redis)**:
   - Configured Celery worker with Redis broker and result backend.
   - Background tasks for heavy workloads, simulation of long-running job lifecycles, and progress polling (`/tasks/run`, `/tasks/{task_id}/status`).
2. **Automated PDF Invoice Generation (ReportLab)**:
   - On-demand and asynchronous PDF generation for completed customer orders.
   - Clean, professional invoice layout with customer address, itemized table, totals, tax, and branding.
   - Endpoints: `POST /orders/{order_id}/invoice` and `GET /orders/{order_id}/invoice/download`.
3. **Bulk Product CSV Import**:
   - Streaming/file-upload processing of bulk catalog CSVs via `POST /admin/products/import-csv` and `POST /products/import-csv`.
   - Comprehensive validation: schema checks, data types, pricing bounds, category defaults, and duplicate prevention.
4. **PostgreSQL Full-Text Search (FTS) & Fuzzy Search**:
   - PostgreSQL `to_tsvector` and `plainto_tsquery` English text search.
   - Trigram similarity (`similarity()`) fuzzy matching with configurable similarity thresholds.
   - Fast, unified search endpoint: `GET /products/search?q={query}`.
5. **Database Migrations with Alembic**:
   - Version-controlled schema migrations under `backend/alembic/`.
   - Migration script creating search indices and trigram extensions (`2fe8b51e35b9_day18_fts_and_fuzzy_search.py`).
6. **Query Optimization & Eager Loading**:
   - Eliminated N+1 query patterns in order retrieval using SQLAlchemy `selectinload` and `joinedload`.
   - Benchmarked endpoints: `GET /orders/optimized` and `GET /admin/orders/optimized`.
7. **Comprehensive Automated Test Suite**:
   - Automated tests across Celery lifecycle, PDF invoices, CSV bulk imports, FTS search, and query optimization.

---

## 2. Tech Stack

- **Backend**: Python 3.14 / 3.13, FastAPI, Uvicorn, SQLAlchemy, Alembic, psycopg3
- **Task Queue & Cache**: Celery, Redis
- **Document Generation**: ReportLab
- **Database**: PostgreSQL (`sqlight` database on port 5432) with SQLite local fallback
- **Frontend**: React 18, TypeScript, Vite, Zustand, Tailwind CSS / Custom CSS
- **Testing**: Pytest, Playwright, Vitest

---

## 3. API Endpoints Summary

### Tasks & Background Jobs
- `POST /tasks/run`: Dispatches an asynchronous multi-step background job via Celery.
- `GET /tasks/{task_id}/status`: Polls progress, status (`PENDING`, `PROGRESS`, `SUCCESS`, `FAILURE`), and result payload.

### Invoices
- `POST /orders/{order_id}/invoice`: Generates a PDF invoice for an order.
- `GET /orders/{order_id}/invoice/download`: Downloads the generated PDF invoice.

### Bulk Import
- `POST /admin/products/import-csv`: Bulk import products from uploaded CSV file with row validation and detailed failure reporting.

### Search
- `GET /products/search?q={query}`: Combined full-text search and fuzzy matching on name, category, and description.

### Optimized Orders
- `GET /orders/optimized`: Customer order history with eager-loaded order items.
- `GET /admin/orders/optimized`: Admin order overview with single-roundtrip joined loading.

---

## 4. Setup & Running Locally

### Start Redis
```powershell
.\redis\redis-server.exe .\redis\redis.windows.conf
```

### Start Celery Worker
```powershell
py -3.14 -m celery -A backend.celery_app.celery_app worker --loglevel=info --pool=solo
```

### Start FastAPI Backend
```powershell
cd backend
py -3.14 -m uvicorn main:app --reload --port 8000
```

### Run Tests
```powershell
pytest tests/
```
