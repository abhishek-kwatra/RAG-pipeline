from fastapi import FastAPI
from backend.routes.upload import router as upload_router
from backend.routes.query import router as query_router
from backend.routes.metadata import router as metadata_router
from backend.config.config import get_connection
from backend.services.weaviate_client import client

app = FastAPI(title="RAG API")

app.include_router(upload_router)
app.include_router(query_router)
app.include_router(metadata_router)

create_tables_sql = """
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    pages INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    doc_id INT REFERENCES documents(id) ON DELETE CASCADE,
    text TEXT,
    vector_id TEXT
);
"""

@app.on_event("startup")
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(create_tables_sql)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables ensured at startup")

@app.get("/")
def root():
    return {"message": "RAG API running"}

@app.on_event("shutdown")
def close_weaviate():
    client.close()
    print("🔒 Weaviate client connection closed")
