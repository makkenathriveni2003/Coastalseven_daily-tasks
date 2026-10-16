# Day 20 – Complete ShopZone AI Shopping Assistant & Full-Stack Platform

Complete full-stack implementation of the **Day 20 ShopZone E-Commerce platform** featuring:
- **AI Shopping Assistant with Multi-Provider Support** (Google Gemini, Groq, Mistral, OpenAI-compatible via `backend/app/services/ai/`)
- **Server-Sent Events (SSE) Real-Time Streaming** (`/api/ai/chat/stream` with real-time UI token updates & AbortController support)
- **Intelligent LLM Fallback Manager** (Seamless failover across configured providers on API timeout, rate limiting, or errors)
- **RAG (Retrieval-Augmented Generation)** (ChromaDB vector store with semantic embeddings strictly grounded in ShopZone's PostgreSQL catalog)
- **Interactive AI Citation Cards** (Rich product previews, in-stock badges, price calculations, and direct Add-to-Cart links)
- **Automated AI Tests** (`backend/tests/test_ai_features.py` and `frontend/src/pages/AiAssistant.test.tsx`)
- **OWASP API Security, SlowAPI Rate Limiting & GZip Response Compression**
- **Frontend Performance Optimization** (Vite 8, Rollup manual chunking, responsive mobile & desktop UI)

---

## 1. Quick Start Commands

### Step 1: Start Redis
```powershell
.\redis\redis-server.exe .\redis\redis.windows.conf
```

### Step 2: Start Celery Background Worker
```powershell
py -3.14 -m celery -A backend.celery_app.celery_app worker --loglevel=info --pool=solo
```

### Step 3: Start FastAPI Backend
```powershell
py -3.14 -m uvicorn app.main:app --app-dir backend --port 8000
```

### Step 4: Start Frontend
```powershell
cd frontend
npm run dev
# or preview the production build:
npm run preview -- --port 4173
```

---

## 2. AI Assistant Configuration & Environment

In `backend/.env`:
```env
AI_PRIMARY_PROVIDER=gemini
AI_FALLBACK_PROVIDERS=groq,mistral,openai
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
```

To re-index the product catalog into ChromaDB:
```powershell
py -3.14 backend/scripts/reindex_catalog.py
```

To run the AI automated test suite:
```powershell
py -3.14 -m pytest backend/tests/test_ai_features.py -v
```
