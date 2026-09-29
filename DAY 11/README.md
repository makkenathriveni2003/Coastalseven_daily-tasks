# Daybook

Daybook is a React task planner backed by a FastAPI API. Accounts use hashed passwords and expiring JWT access tokens. Tasks are stored in SQLite and are isolated by account.

## Requirements

- Node.js 18.18 or newer
- Python 3.11 or newer

## Run the API

From the project root, install the Python dependencies and start FastAPI:

```powershell
py -3.13 -m pip install -r backend/requirements.txt
$env:JWT_SECRET_KEY = "replace-with-a-long-random-secret"
py -3.13 -m uvicorn backend.main:app --reload --port 8000
```

The API and interactive schema are available at `http://127.0.0.1:8000` and `http://127.0.0.1:8000/docs`. The SQLite database is created at `backend/daybook.sqlite3` on first start.

## Run the React app

In a second terminal:

```powershell
npm install
npm run dev
```

Vite proxies `/api` requests to `http://127.0.0.1:8000`. Open the URL printed by Vite, create an account, and add tasks. The token is stored in browser local storage; task data stays in SQLite.

## Pages

- `/` - Home
- `/login` - Sign in
- `/register` - Create an account
- `/dashboard` - Protected task dashboard
- `/dashboard/add-task` - Protected task creation page
- `/dashboard/tasks/{task_id}` - Protected task details

Set `VITE_API_BASE_URL` to a full API base URL when running the frontend outside Vite's development proxy. Backend settings can be configured with `JWT_SECRET_KEY`, `ACCESS_TOKEN_MINUTES`, `CORS_ORIGINS`, and `DATABASE_PATH`.
