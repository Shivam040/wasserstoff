import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from uuid import uuid4

client = chromadb.Client()
collection = client.get_or_create_collection(name="docs")

embedder = OpenAIEmbeddingFunction(
    api_key="your-openai-key-if-used",  # If needed, else use SentenceTransformers
    model_name="text-embedding-ada-002"
)

def add_to_vectorstore(text_chunks: list[str], metadatas: list[dict]):
    ids = [str(uuid4()) for _ in text_chunks]
    collection.add(documents=text_chunks, metadatas=metadatas, ids=ids)

def query_vectorstore(query: str, top_k=5):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results['documents'][0]  # return top-k chunks
