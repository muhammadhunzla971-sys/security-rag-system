from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Step 1: Load the document
loader = TextLoader("../data/sample_docs.txt")
documents = loader.load()
print(f"✅ Document loaded: {len(documents)} document(s)")

# Step 2: Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(documents)
print(f"✅ Split into {len(chunks)} chunks")

# Step 3: Create embeddings
print("⏳ Loading embedding model (may take a minute first time)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
print("✅ Embedding model loaded")

# Step 4: Store in vector database
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="../chroma_db")
print("✅ Vector database created")

# Step 5: Test a query
query = "What is SQL injection?"
results = vectorstore.similarity_search(query, k=2)

print("\n🔍 Query:", query)
print("\n📄 Top matching chunks:")
for i, doc in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content)