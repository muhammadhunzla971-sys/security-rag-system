import os
from dotenv import load_dotenv
from groq import Groq
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load API key from .env
load_dotenv("../.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Step 1: Load and prepare vector database (same as before)
loader = TextLoader("../data/sample_docs.txt")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="../chroma_db")
print("✅ Vector database ready")

# Step 2: Take a question
query = "What is SQL injection and how do you prevent it?"

# Step 3: Retrieve relevant chunks
results = vectorstore.similarity_search(query, k=2)
context = "\n\n".join([doc.page_content for doc in results])
print("✅ Retrieved relevant context")
print("\n--- DEBUG: Actual context sent to LLM ---")
print(context)
print("--- END DEBUG ---\n")
# Step 4: Build the prompt
prompt = f"""You are a cybersecurity expert assistant. Use the context below to answer the question as helpfully as possible.

Context:
{context}

Question: {query}

Answer:"""

# Step 5: Send to LLM
print("⏳ Generating answer...")
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

answer = response.choices[0].message.content
print("\n🤖 Final Answer:\n")
print(answer)