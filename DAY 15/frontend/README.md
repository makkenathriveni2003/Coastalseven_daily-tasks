# Daylight shop

A responsive, type-safe React storefront built with TypeScript, Vite, React
Router, Zustand, and TanStack Query. It has a Vitest/React Testing Library
component suite with MSW API mocks and a Playwright end-to-end test.

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
- The light/dark theme toggle saves the selected theme in browser local storage.
- TanStack Query caches product pages and requests additional pages as the
  product list is scrolled.
- The FastAPI product catalog includes dresses, jewelry, and original
  cinema-inspired graphic shirts alongside the existing categories.
- Product and cart routes are lazy-loaded. Product cards are memoized and
  product images are lazy-loaded with responsive image parameters.

## Lighthouse

Run Lighthouse against the production build rather than Vite's development
server, which includes development-only tooling and can inflate JavaScript and
main-thread measurements:

```powershell
npm run build
npm run preview
```

Open `http://127.0.0.1:4173/` for the audit.

## Verify changes

Run these commands from `frontend`:

```powershell
npm run typecheck
npm run lint
npm test
npx playwright install chromium
npm run test:e2e
npm run build
```

Component tests use MSW and do not need a running FastAPI server. The Playwright
test also mocks the product API, so it exercises the storefront journey without
depending on a live backend. GitHub Actions runs type checking, linting,
component tests, Playwright, and the production build on frontend changes.
