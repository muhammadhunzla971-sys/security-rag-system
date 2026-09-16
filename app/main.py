from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

from app.rag.pipeline import RAGPipeline
from app.api.auth import verify_api_key

app = FastAPI(title="Security RAG API")
Instrumentator().instrument(app).expose(app)
# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

rag = RAGPipeline()

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "Security RAG API is running"}

@app.post("/ask")
@limiter.limit("5/minute")
def ask_question(request: Request, body: QueryRequest, tenant: str = Depends(verify_api_key)):
    result = rag.answer_query(body.question)
    result["tenant"] = tenant
    return result