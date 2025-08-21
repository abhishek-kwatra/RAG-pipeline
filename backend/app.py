from fastapi import FastAPI
from backend.routes.upload import router as upload_router
from backend.routes.query import router as query_router
from backend.routes.metadata import router as metadata_router
from backend.services.weaviate_client import client

app = FastAPI(title="RAG API")

app.include_router(upload_router)
app.include_router(query_router)
app.include_router(metadata_router)

@app.get("/")
def root():
    return {"message": "RAG API running"}

@app.on_event("shutdown")
def close_weaviate():
    client.close()
    print("🔒 Weaviate client connection closed")
