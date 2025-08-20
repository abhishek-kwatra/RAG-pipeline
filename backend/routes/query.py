from fastapi import APIRouter
from backend.services.embeddings import  search_chunks 
from backend.utils.llm import ask_llm
import numpy as np

router = APIRouter()

@router.post("/query")
async def query_doc(question: str):
    retrieved = search_chunks(question)  # removed chunk_store
    context = "\n".join(retrieved)
    answer = ask_llm(context, question)
    return {"answer": answer, "context": retrieved}
