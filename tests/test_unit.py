from backend.services.embeddings import chunk_text, embed_chunks
import numpy as np


def test_chunk_text():
    text = "Hello World! " * 50
    chunks = chunk_text(text, size=20)

    assert all(len(c) <= 20 for c in chunks)
    assert "".join(chunks) == text
    
def test_chunk_text_empty():
    chunks = chunk_text("", size=5)
    assert chunks == []
    
def test_embed_chunks_shape():
    sample_chunks = ["Hello Company", "This is a user 1 doing testing"]
    vectors = embed_chunks(sample_chunks)

    assert isinstance(vectors, np.ndarray)
    assert vectors.shape[0] == len(sample_chunks)
    assert vectors.shape[1] > 0   # embedding dimension

