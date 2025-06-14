from uuid import uuid4
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Using a pre-trained sentence transformer model for embeddings
model = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Initialize Chroma client and get/create a collection named "docs"
client = chromadb.Client()
collection = client.get_or_create_collection(
    name="docs",
    embedding_function=model
)


def add_to_vectorstore(text_chunks: list[str], metadatas: list[dict]):
    """
    Adds a list of text chunks and their corresponding metadata to the Chroma vectorstore.

    Args:
        text_chunks (list[str]): List of strings representing the text chunks to embed and store.
        metadatas (list[dict]): List of metadata dictionaries corresponding to each chunk.
    """
    ids = [str(uuid4()) for _ in text_chunks]
    collection.add(
        documents=text_chunks,
        metadatas=metadatas,
        ids=ids,
    )

def query_vectorstore(query: str, top_k=5):
    """
    Queries the Chroma vectorstore with a natural language query and retrieves the top-k matching documents.

    Args:
        query (str): The search query string.
        top_k (int, optional): Number of top matching chunks to return. Defaults to 5.

    Returns:
        list[dict]: A list of dictionaries with 'text' and 'metadata' keys for the top matching chunks.
    """
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


