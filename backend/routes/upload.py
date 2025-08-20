from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz
import uuid
from backend.services.embeddings import embed_chunks, chunk_text
from backend.services.weaviate_client import client, chunk_schema
from backend.config.config import get_connection

router = APIRouter()

@router.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="You can upload a maximum of 20 PDF files at once.")

    chunk_schema()
    total_chunks = 0
    collection = client.collections.get("DocumentChunk")

    conn = get_connection()
    cur = conn.cursor()

    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF file.")

        # Check if file already exists
        cur.execute("SELECT id FROM documents WHERE filename = %s;", (file.filename,))
        existing_doc = cur.fetchone()
        if existing_doc:
            cur.close()
            conn.close()
            return {"message": f"File {file.filename} is already present."}

        pdf_data = await file.read()
        with fitz.open(stream=pdf_data, filetype="pdf") as doc:
            if len(doc) > 1000:
                raise HTTPException(status_code=400, detail=f"{file.filename} has more than 1000 pages.")

            text = "".join([page.get_text() for page in doc])

            # Insert new document
            cur.execute(
                "INSERT INTO documents (filename, pages) VALUES (%s, %s) RETURNING id;",
                (file.filename, len(doc))
            )
            document_id = cur.fetchone()["id"]

        chunks = chunk_text(text)
        embeddings = embed_chunks(chunks)

        for chunk, embedding in zip(chunks, embeddings):
            new_id = str(uuid.uuid4())
            
            # Insert into Weaviate
            collection.data.insert(
                properties={"text": chunk, "source": file.filename},
                vector=embedding,
                uuid=new_id
            )

            # Insert into chunks table
            cur.execute(
                "INSERT INTO chunks (doc_id, text, vector_id) VALUES (%s, %s, %s);",
                (document_id, chunk, new_id)
            )

        total_chunks += len(chunks)

    conn.commit()
    cur.close()
    conn.close()

    return {
        "message": "Files processed successfully.",
        "total_files": len(files),
        "total_chunks": total_chunks
    }
