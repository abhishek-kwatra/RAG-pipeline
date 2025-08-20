from sentence_transformers import SentenceTransformer
import numpy as np
from backend.services.weaviate_client import client

model = SentenceTransformer("all-MiniLM-L6-v2")
chunks = []

def embed_chunks(chunks: list[str]):
    vectors = model.encode(chunks)
    return np.array(vectors).astype("float32")


def chunk_text(text: str, size: int = 100) -> list[str]:
    return [text[i:i+size] for i in range(0, len(text), size)]


def add_document(text: str):
    global chunks
    new_chunks = chunk_text(text)
    embeddings = model.encode(new_chunks)
    chunks.extend(new_chunks)

def search_chunks(query: str, k: int = 3):
    query_chunks = chunk_text(query, size=100)
    all_texts = []

    for q_chunk in query_chunks:
        q_vec = model.encode([q_chunk]).astype("float32")[0]

        response = client.collections.get("DocumentChunk").query.near_vector(
            near_vector=q_vec,
            limit=10
        )
        print(response);
        all_texts.extend(obj.properties.get("text", "") for obj in response.objects)

    seen = set()
    unique_texts = []
    for text in all_texts:
        if text not in seen:
            seen.add(text)
            unique_texts.append(text)

    return unique_texts[:k]
