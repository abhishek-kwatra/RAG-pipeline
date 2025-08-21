from fastapi import APIRouter, HTTPException
from backend.config.config import supabase  
router = APIRouter()

@router.get("/metadata/{filename}")
async def get_file_metadata(filename: str):
    try:
        response = supabase.table("documents").select("id, filename, pages").eq("filename", filename).execute()
        docs = response.data 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not docs or len(docs) == 0:
        raise HTTPException(status_code=404, detail=f"No document found with filename: {filename}")

    doc = docs[0]
    doc_id = doc["id"]

    try:
        chunk_resp = supabase.table("chunks").select("id", count="exact").eq("doc_id", doc_id).execute()
        chunk_count = chunk_resp.count if chunk_resp.count is not None else 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "filename": doc["filename"],
        "pages": doc["pages"],
        "chunks": chunk_count
    }
