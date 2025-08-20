import os
import weaviate
from weaviate.classes.config import Property, DataType
from dotenv import load_dotenv


load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY)
)


def chunk_schema():
    if not client.collections.exists("DocumentChunk"):
        client.collections.create(
            name="DocumentChunk",
            properties=[
                Property(name="text", data_type=DataType.TEXT),
                Property(name="source", data_type=DataType.TEXT),
            ],
            vectorizer_config=None  # important: since you don’t use OpenAI vectorizer
        )


def insert_chunk(chunk: str, source: str, vector: list[float]):
    collection = client.collections.get("DocumentChunk")
    collection.data.insert(
        properties={
            "text": chunk,
            "source": source,
        },
        vector=vector  
    )


def close_weaviate_client():
    if client.is_connected():
        client.close()
        print("✅ Weaviate client connection closed.")