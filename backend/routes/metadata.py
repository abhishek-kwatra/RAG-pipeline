from fastapi import APIRouter, HTTPException
from backend.config.config import get_connection

router = APIRouter()

@router.get("/metadata/{filename}")
async def get_file_metadata(filename: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, filename, pages FROM documents WHERE filename = %s;", (filename,))
    doc = cur.fetchone()

    if not doc:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"No document found with filename: {filename}")

    doc_id = doc["id"]

    cur.execute("SELECT COUNT(*) as chunk_count FROM chunks WHERE doc_id = %s;", (doc_id,))
    chunk_count = cur.fetchone()["chunk_count"]

    cur.close()
    conn.close()

    return {
        "filename": doc["filename"],
        "pages": doc["pages"],
        "chunks": chunk_count
    }
