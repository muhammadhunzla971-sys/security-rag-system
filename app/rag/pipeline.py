import os
import json
import hashlib
from dotenv import load_dotenv
from groq import Groq
import redis
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

class RAGPipeline:
    def __init__(self):
        print("⏳ Initializing RAG pipeline...")
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        loader = TextLoader("data/sample_docs.txt")
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = Chroma.from_documents(chunks, self.embeddings, persist_directory="chroma_db")

        # Redis connection
        import os
        self.redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)
        print("✅ RAG pipeline ready")

    def _cache_key(self, query: str) -> str:
        # Query ko hash karo taake ek chhoti, safe cache key bane
        return "rag_cache:" + hashlib.md5(query.lower().strip().encode()).hexdigest()

    def answer_query(self, query: str) -> dict:
        cache_key = self._cache_key(query)

        # Step 1: Redis mein check karo
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            result = json.loads(cached_result)
            result["cached"] = True
            return result

        # Step 2: Cache mein nahi mila, to RAG pipeline chalao
        results = self.vectorstore.similarity_search(query, k=2)
        context = "\n\n".join([doc.page_content for doc in results])

        prompt = f"""You are a cybersecurity expert assistant. Use the context below to answer the question as helpfully as possible.

Context:
{context}

Question: {query}

Answer:"""

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        result = {
            "query": query,
            "answer": response.choices[0].message.content,
            "sources_used": len(results),
            "cached": False
        }

        # Step 3: Result ko Redis mein save karo (1 hour ke liye)
        self.redis_client.setex(cache_key, 3600, json.dumps(result))

        return result