from fastapi import APIRouter, UploadFile, File, Form
from app.services.extractor import extract_text_from_file
from app.services.embedder import add_to_vectorstore, query_vectorstore
from app.services.groq_llm import get_answer_from_llama

router = APIRouter()

@router.post("/upload/")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    path = f"backend/data/{file.filename}"
    with open(path, "wb") as f:
        f.write(content)

    text = extract_text_from_file(path)
    # simple chunking:
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    metadatas = [{"filename": file.filename, "chunk_id": i} for i in range(len(chunks))]

    add_to_vectorstore(chunks, metadatas)
    return {"status": "uploaded", "chunks": len(chunks)}

@router.post("/query/")
async def query(query: str = Form(...)):
    contexts = query_vectorstore(query)
    answer = get_answer_from_llama(query, contexts)
    return {"answer": answer, "sources": contexts}
