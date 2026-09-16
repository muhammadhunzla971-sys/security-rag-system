# 🛡️ Security RAG System

A production-grade **Retrieval-Augmented Generation (RAG)** chatbot that answers cybersecurity questions using a curated knowledge base of CVEs, attack patterns, and security best practices — backed by a full observability and caching stack.

Built and deployed end-to-end: local development → Dockerized services → CI-friendly GitHub repo → cloud deployment on Railway.

**🔗 Live API:** `https://security-rag-system-production.up.railway.app/docs`

---

## ✨ Features

- **Retrieval-Augmented Generation** — combines semantic search over a cybersecurity document store with an LLM to produce grounded, context-aware answers instead of generic hallucinated responses.
- **Multi-tenant API key authentication** — each request is authenticated via an `x-api-key` header, with per-tenant identification in the response.
- **Rate limiting** — protects the API from abuse using `slowapi` (5 requests/minute per client).
- **Redis-backed response caching** — identical questions are served from cache (`"cached": true`), cutting latency and LLM API costs on repeated queries.
- **Full observability** — Prometheus metrics exposed at `/metrics`, visualized in a custom Grafana dashboard (Total Requests, Average Response Time, Error Count).
- **Containerized & cloud-deployed** — Docker Compose orchestrates the app, Redis, Prometheus, and Grafana; the app service is deployed to Railway with a managed Redis instance.

---

## 🏗️ Architecture

```
                        ┌─────────────┐
                        │   Client    │
                        └──────┬──────┘
                               │  x-api-key + question
                               ▼
                     ┌───────────────────┐
                     │   FastAPI Server   │
                     │  (auth + rate      │
                     │   limiting)        │
                     └─────────┬─────────┘
                               │
                 ┌─────────────┼─────────────┐
                 ▼                            ▼
        ┌────────────────┐          ┌──────────────────┐
        │  Redis Cache    │◄────────►│   RAG Pipeline    │
        │ (query → answer)│          │                   │
        └────────────────┘          │ ChromaDB (vector  │
                                     │ store) + Hugging   │
                                     │ Face embeddings    │
                                     └─────────┬─────────┘
                                               │ retrieved context
                                               ▼
                                     ┌───────────────────┐
                                     │   Groq LLM API     │
                                     │ (openai/gpt-oss-20b)│
                                     └───────────────────┘

        Prometheus  ──scrapes metrics──►  Grafana Dashboard
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| LLM inference | Groq API (`openai/gpt-oss-20b`) |
| Vector store | ChromaDB |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| Caching | Redis |
| Auth & rate limiting | Custom API key middleware + `slowapi` |
| Monitoring | Prometheus + Grafana |
| Containerization | Docker & Docker Compose |
| Deployment | Railway |

---

## 📡 API Endpoints

### `POST /ask`
Ask a cybersecurity question and get a grounded, LLM-generated answer.

**Headers**
```
x-api-key: <your-api-key>
Content-Type: application/json
```

**Request body**
```json
{
  "question": "What is a SQL injection attack?"
}
```

**Response**
```json
{
  "query": "What is a SQL injection attack?",
  "answer": "A SQL injection attack is a type of cyber-attack in which an attacker deliberately inserts malicious SQL code into an input field...",
  "sources_used": 2,
  "cached": false,
  "tenant": "Tenant One"
}
```

### `GET /metrics`
Prometheus-formatted metrics for request count, latency, and errors.

### `GET /`
Health check / welcome endpoint.

---

## 🚀 Getting Started (Local Setup)

### Prerequisites
- Docker & Docker Compose
- A [Groq API key](https://console.groq.com/keys)

### 1. Clone the repo
```bash
git clone https://github.com/muhammadhunzla971-sys/security-rag-system.git
cd security-rag-system
```

### 2. Configure environment variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
REDIS_HOST=redis
REDIS_PORT=6379
```

### 3. Run with Docker Compose
```bash
docker-compose up --build
```

This spins up four services:
- `app` — the FastAPI application (port `8000`)
- `redis` — caching layer
- `prometheus` — metrics collection
- `grafana` — dashboards (default login: `admin` / `admin123`)

### 4. Try it out
Open `http://localhost:8000/docs` for interactive Swagger UI, or:
```bash
curl -X POST 'http://localhost:8000/ask' \
  -H 'x-api-key: tenant1-secret-key-123' \
  -H 'Content-Type: application/json' \
  -d '{"question": "What is a SQL injection attack?"}'
```

---

## ☁️ Deployment

The production instance runs on **Railway**, with:
- The FastAPI app service built directly from this GitHub repo
- A Railway-managed Redis instance (connected via `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` service variables)
- Environment variables (`GROQ_API_KEY`, Redis credentials) configured through Railway's Variables tab
- A public domain auto-generated by Railway for HTTPS access

---

## 📌 Project Notes

- Demo API keys (`tenant1-secret-key-123`, `tenant2-secret-key-456`) are provided for testing multi-tenant behavior — replace with real key management in a production setting.
- The knowledge base currently covers a sample set of cybersecurity documents; it's designed to be easily extended with more CVE data and security documentation.

---

## 📄 License

This project is open for educational and portfolio purposes.
