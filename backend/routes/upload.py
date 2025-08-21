from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz
import uuid
from backend.services.embeddings import embed_chunks, chunk_text
from backend.services.weaviate_client import client, chunk_schema
from backend.config.config import supabase  
router = APIRouter()

@router.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="You can upload a maximum of 20 PDF files at once.")

    chunk_schema()
    total_chunks = 0
    collection = client.collections.get("DocumentChunk")

    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF file.")

        existing_doc = supabase.table("documents").select("id").eq("filename", file.filename).execute()
        if existing_doc.data:
            return {"message": f"File {file.filename} is already present."}

        pdf_data = await file.read()
        with fitz.open(stream=pdf_data, filetype="pdf") as doc:
            if len(doc) > 1000:
                raise HTTPException(status_code=400, detail=f"{file.filename} has more than 1000 pages.")

            text = "".join([page.get_text() for page in doc])

            insert_doc = supabase.table("documents").insert({
                "filename": file.filename,
                "pages": len(doc)
            }).execute()

            document_id = insert_doc.data[0]["id"]

        chunks = chunk_text(text)
        embeddings = embed_chunks(chunks)

        for chunk, embedding in zip(chunks, embeddings):
            new_id = str(uuid.uuid4())

            collection.data.insert(
                properties={"text": chunk, "source": file.filename},
                vector=embedding,
                uuid=new_id
            )

            supabase.table("chunks").insert({
                "doc_id": document_id,
                "text": chunk,
                "vector_id": new_id
            }).execute()

        total_chunks += len(chunks)

    return {
        "message": "Files processed successfully.",
        "total_files": len(files),
        "total_chunks": total_chunks
    }
