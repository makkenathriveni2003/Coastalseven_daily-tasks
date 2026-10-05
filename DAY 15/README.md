# Day 15 — TypeScript for React & Component Testing

This is the standalone Day 15 project, separated from the Day 14 workspace.

## Project folders

- `frontend/` — TypeScript React storefront, MSW-backed component tests, and
  Playwright end-to-end tests.
- `backend/` — FastAPI product API used by the storefront, with electronics,
  accessories, dresses, jewelry, and original graphic shirts.
- `.github/workflows/` — CI workflow for frontend checks.

To install and run the frontend, open a terminal in `frontend` and run
`npm ci`, then use the commands in `frontend/README.md` to type-check, lint,
test, and build the app.

The storefront includes a light/dark theme toggle and remembers the selected
theme in the browser.
