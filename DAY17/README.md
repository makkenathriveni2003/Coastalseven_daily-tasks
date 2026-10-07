# Day 17 — ShopZone Real-Time E-Commerce (End-to-End)

Complete, fully working full-stack implementation of the **Day 17 ShopZone E-Commerce platform** featuring real-time WebSocket communication, PostgreSQL database integration, JWT authentication, automatic exponential-backoff reconnection, live order updates, real-time notifications panel, and Admin ↔ Customer live chat.

---

## 1. Day 17 Objective

Build and integrate end-to-end real-time capabilities on top of the ShopZone e-commerce application:
1. **CORS & Environment Configuration**: Configured FastAPI CORS and environment variables for seamless React ↔ FastAPI REST and WebSocket communication.
2. **JWT Authentication**: Secure login, token storage, authorized API requests, role protection (`shopper` vs `admin`), and clean 401/403 handling.
3. **Reusable `useWebSocket` Hook**: Clean, encapsulated React hook managing connection lifecycle, messages, errors, and cleanup.
4. **WebSocket Automatic Reconnection**: Exponential backoff with capped retry delay and max retries preventing infinite reconnect loops.
5. **Live Order Updates**: Status changes made by administrators update the customer's order history in real time with zero page refresh.
6. **Real-Time Notifications**: Floating notification panel with unread badge counter displaying order lifecycle events (`confirmed`, `processing`, `shipped`, `delivered`, `cancelled`).
7. **Admin ↔ Customer Live Chat**: Full-duplex instant chat between shoppers and administrators with DB persistence and live WebSocket broadcast.
8. **PostgreSQL + pgAdmin Integration**: Safely connected to PostgreSQL instance on port 5432 (database `sqlight`), verified table schemas, preserved data, and tested DB-backed operations.

---

## 2. Features Implemented

- ✅ **Storefront & Product Catalog**: 16 products loaded directly from PostgreSQL database.
- ✅ **Instant Search & Category Filtering**: Client-side instant search input filtering products by name or category with clear button.
- ✅ **Shopping Bag & Global Cart**: Zustand state management with persistent storage and item quantity controls.
- ✅ **Dark / Light Mode**: Dynamic theme switcher with localStorage persistence and CSS custom variables.
- ✅ **JWT Authentication Flow**:
  - `POST /auth/login` returning signed HS256 JWT access token.
  - `POST /auth/register` creating user accounts with PBKDF2-SHA256 password hashing.
  - `GET /auth/me` protected endpoint returning authenticated profile and role.
  - Frontend `authStore` managing tokens in sessionStorage and auto-injecting Bearer tokens.
- ✅ **Reusable `useWebSocket` Hook**:
  - Encapsulated lifecycle: `connect()`, `disconnect()`, `sendMessage()`, `status`, `reconnectAttempts`.
  - Exponential backoff: `delay = Math.min(baseDelay * 2^(attempt-1), maxDelay)`.
  - Header status pill: Live (green), Reconnecting (amber with retry count), Offline (red with retry button).
- ✅ **Live Order Updates**:
  - When customer places an order via `POST /orders`, broadcast event is sent to admins and customer.
  - When admin updates order status via `PATCH /admin/orders/{id}/status`, customer order history automatically updates with 0ms manual reload.
- ✅ **Real-Time Notifications Panel**:
  - Bell icon in header with unread count badge.
  - Popover drawer displaying events: Order Confirmed, Order Processing, Order Shipped, Order Delivered, Order Cancelled.
  - Read/unread state management, "Mark all read", and "Clear" actions.
- ✅ **Admin ↔ Customer Live Chat**:
  - Floating Live Chat widget with connection dot and unread badge.
  - Real-time full-duplex communication over WebSocket with database persistence in `chat_messages` table.
  - Admin view with customer conversation switching and customer view chatting with Support.
  - REST fallback endpoints `GET /chat/messages` and `POST /chat/messages`.

---

## 3. Folder Structure

```text
Downloads/day17/
├── backend/
│   ├── routers/
│   │   ├── orders.py
│   │   └── products.py
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── requirements.txt
│   ├── schemas.py
│   └── websocket_manager.py
├── frontend/
│   ├── e2e/
│   │   ├── day17-features.spec.ts
│   │   ├── live-integration.spec.ts
│   │   └── storefront.spec.ts
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── LiveChatWidget.test.tsx
│   │   │   ├── LiveChatWidget.tsx
│   │   │   ├── NotificationsPanel.test.tsx
│   │   │   ├── NotificationsPanel.tsx
│   │   │   └── ProductCard.tsx
│   │   ├── hooks/
│   │   │   ├── useIntersectionObserver.ts
│   │   │   ├── useProducts.ts
│   │   │   ├── useWebSocket.test.ts
│   │   │   └── useWebSocket.ts
│   │   ├── pages/
│   │   │   ├── AdminDashboard.test.tsx
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── Cart.tsx
│   │   │   ├── Checkout.test.tsx
│   │   │   ├── Checkout.tsx
│   │   │   ├── ManageProducts.tsx
│   │   │   ├── OrderHistory.test.tsx
│   │   │   ├── OrderHistory.tsx
│   │   │   ├── ProductDetails.test.tsx
│   │   │   ├── ProductDetails.tsx
│   │   │   ├── Products.test.tsx
│   │   │   └── Products.tsx
│   │   ├── services/
│   │   │   ├── apiClient.test.ts
│   │   │   ├── apiClient.ts
│   │   │   ├── authService.ts
│   │   │   ├── chatService.ts
│   │   │   ├── orderService.ts
│   │   │   └── productService.ts
│   │   ├── store/
│   │   │   ├── authStore.ts
│   │   │   ├── cartStore.test.ts
│   │   │   ├── cartStore.ts
│   │   │   ├── chatStore.test.ts
│   │   │   ├── chatStore.ts
│   │   │   ├── notificationStore.test.ts
│   │   │   └── notificationStore.ts
│   │   ├── test/
│   │   │   ├── handlers.ts
│   │   │   ├── products.ts
│   │   │   ├── server.ts
│   │   │   ├── setupTests.ts
│   │   │   └── testUtils.tsx
│   │   ├── utils/
│   │   │   └── queryClient.ts
│   │   ├── App.css
│   │   ├── App.test.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── main.tsx
│   │   └── types.ts
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── package.json
│   ├── playwright.config.ts
│   ├── tsconfig.json
│   └── vite.config.ts
├── tests/
│   ├── conftest.py
│   ├── test_auth_and_jwt.py
│   ├── test_orders_and_live_updates.py
│   ├── test_products_api.py
│   └── test_websocket_and_chat.py
├── .gitignore
└── README.md
```

---

## 4. Tech Stack

- **Backend**: FastAPI, Uvicorn, Python 3.14, WebSockets, Psycopg (PostgreSQL driver 3.3.6), Pydantic v2, Python-dotenv, Pytest.
- **Frontend**: React 19, TypeScript 5.9, Vite 8.3, TanStack React Query v5, Zustand v5, React Hook Form, Zod.
- **Testing**: Vitest, React Testing Library, MSW (Mock Service Worker v2 with WebSocket link), Playwright.
- **Database**: PostgreSQL 18 (service `postgresql-x64-18` on port 5432), pgAdmin 4.

---

## 5. Environment Setup

### Backend `.env` (`backend/.env`)
```env
DATABASE_ENGINE=postgres
PGHOST=127.0.0.1
PGPORT=5432
PGDATABASE=sqlight
PGUSER=Thriveni
PGPASSWORD=23660C7CF12D93563E7206F4311DEC1CB47633E8D31C1755539A9215FE53A6D5A8BCBAB05A85957F
JWT_SECRET_KEY=fZr7Wf-hO_iq7j3rM0ripJd0fidB7OoxeXV3Ur_OJQcqArNurmt_GLIEKpN7EB4o
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:4173,http://127.0.0.1:4173,http://localhost:3000,http://127.0.0.1:3000
```

### Frontend `.env` (`frontend/.env`)
```env
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000/ws
```

---

## 6. PostgreSQL & pgAdmin Setup

- **Service Name**: `postgresql-x64-18` (Running)
- **Port**: `5432`
- **Host**: `127.0.0.1`
- **Database**: `sqlight`
- **User**: `Thriveni`
- **pgAdmin**: Installed at `C:\Program Files\pgAdmin 4\runtime\pgAdmin4.exe`.
- **Tables Present & Initialized**:
  - `products`: Catalog items (16 seeded items preserved).
  - `users`: Shopper & Admin user accounts.
  - `orders`: Customer orders.
  - `order_items`: Order line items with snapshots.
  - `chat_messages`: Persisted real-time live chat messages.

---

## 7. Run Commands (In VS Code)

### Terminal 1 — Backend
```powershell
cd Downloads\day17\backend
& ..\..\day15\.venv\Scripts\uvicorn.exe main:app --host 127.0.0.1 --port 8000 --reload
```
API runs at `http://127.0.0.1:8000`  
Interactive Swagger docs: `http://127.0.0.1:8000/docs`

### Terminal 2 — Frontend
```powershell
cd Downloads\day17\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
Frontend runs at `http://127.0.0.1:5173`

---

## 8. JWT Authentication Flow

```text
User signs in (/auth/login)
          ↓
Backend verifies PBKDF2 hash & creates HS256 JWT
          ↓
Frontend authStore saves token & user in sessionStorage
          ↓
Subsequent API calls attach `Authorization: Bearer <token>`
          ↓
FastAPI Depends(require_authenticated_user) decodes & validates token
          ↓
401 Unauthorized automatically logs out and resets session if expired
```

---

## 9. WebSocket Architecture & Flow

```text
Browser React App (useWebSocket hook)
          ↓ (Connect: ws://127.0.0.1:8000/ws?token=<jwt>)
FastAPI WebSocket endpoint in main.py
          ↓
ConnectionManager validates token, accepts connection
          ↓
Client receives `CONNECTION_ESTABLISHED` + presence data
          ↓
Bidirectional events:
  • ORDER_UPDATE
  • NOTIFICATION
  • CHAT_MESSAGE
  • PING / PONG
```

---

## 10. Reconnection Approach (Exponential Backoff)

When a connection is lost unexpectedly (`event.code !== 1000`):
1. **Initial Retry**: Delay = `baseDelay` (1,000ms).
2. **Subsequent Retries**: `delay = Math.min(baseDelay * Math.pow(2, attempt - 1), maxDelay)`
   - Attempt 1: 1,000ms
   - Attempt 2: 2,000ms
   - Attempt 3: 4,000ms
   - Attempt 4: 8,000ms
   - Attempt 5+: 16,000ms (capped at `maxDelay`)
3. **Cap & Protection**: `maxRetries = 8` prevents uncontrolled infinite loops.
4. **Reset**: As soon as connection opens successfully (`ws.onopen`), `retryCount` resets to 0.

---

## 11. Live Order & Notification Flow

```text
1. Customer submits order (POST /orders)
2. Backend saves order to PostgreSQL
3. ConnectionManager broadcasts ORDER_UPDATE & "Order Confirmed" NOTIFICATION
4. Admin changes order status (PATCH /admin/orders/{id}/status)
5. Backend updates DB row
6. WebSocket event broadcasted to customer & admin
7. Customer React TanStack Query invalidates cache -> UI updates immediately without refresh!
8. Notification bell badge increments & notification card appears in panel.
```

---

## 12. Admin ↔ Customer Chat Flow

```text
Customer sends message via LiveChatWidget
              ↕
WebSocket event { type: "CHAT_MESSAGE", text: "...", recipient: "admin" }
              ↕
FastAPI records message in `chat_messages` table in PostgreSQL
              ↕
ConnectionManager broadcasts to all connected Admin dashboards
              ↕
Admin replies directly to customer email
              ↕
Customer receives message instantly in chat widget without page reload
```

---

## 13. Testing Commands & Results

### Backend Pytest Suite
```powershell
cd Downloads\day17
& ..\day15\.venv\Scripts\python.exe -m pytest tests -v
```
**Result**: `14 passed, 100% success rate`

### Frontend Vitest Suite
```powershell
cd Downloads\day17\frontend
npm test
```
**Result**: `13 test files passed, 68 tests passed, 100% success rate`

### Frontend Playwright E2E Suite
```powershell
cd Downloads\day17\frontend
npx playwright test
```
**Result**: `4 passed (storefront, search/notifications/chat, theme toggle, and full live integration)`

### Frontend Production Build
```powershell
cd Downloads\day17\frontend
npm run build
```
**Result**: `✓ built in 418ms with 0 errors`

---

## 14. Problems Faced & Fixes Applied

1. **Problem**: PostgreSQL connection failed when importing `database.py` alone (`fe_sendauth: no password supplied`).  
   **Fix**: Added `load_dotenv(Path(__file__).with_name(".env"))` directly to `database.py` so environment variables are always loaded regardless of import source.
2. **Problem**: `AttributeError: 'Connection' object has no attribute 'executemany'` in `main.py` when inserting order items with PostgreSQL (psycopg 3).  
   **Fix**: Replaced `connection.executemany` with `connection.execute` loop which is fully supported across both psycopg and sqlite wrappers.
3. **Problem**: `TypeError: Cannot assign to read only property 'WebSocket'` in Vitest.  
   **Fix**: Switched to Vitest's `vi.stubGlobal("WebSocket", MockWebSocket)` and `vi.unstubAllGlobals()`.
4. **Problem**: `scrollIntoView is not a function` in jsdom for the chat widget.  
   **Fix**: Used optional chaining `messagesEndRef.current?.scrollIntoView?.({ behavior: "smooth" })`.
5. **Problem**: Duplicate welcome frames causing race condition in WebSocket integration test.  
   **Fix**: Unified welcome frame dispatch inside `ConnectionManager.connect()` before presence broadcast.
