import os
# from dotenv import load_dotenv
from uuid import uuid4
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# embedder = OpenAIEmbeddingFunction(
#     api_key=OPENAI_API_KEY,
#     model_name="text-embedding-ada-002"
# )

from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

model = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection(
    name="docs",
    embedding_function=model
)

# client = chromadb.Client()
# collection = client.get_or_create_collection(
#     name="docs",
#     embedding_function=embedder  # ✅ attach here instead
# )

def add_to_vectorstore(text_chunks: list[str], metadatas: list[dict]):
    ids = [str(uuid4()) for _ in text_chunks]
    collection.add(
        documents=text_chunks,
        metadatas=metadatas,
        ids=ids,
    )

def query_vectorstore(query: str, top_k=5):
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


