from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.extractor import extract_text_from_file
from app.services.embedder import add_to_vectorstore, query_vectorstore
from app.models.schemas import QueryRequest, QueryResponse, DocumentAnswer, ThemeSummary
from app.services.groq_llm import get_answer_and_themes
import os

router = APIRouter()
uploaded_files_set = set()


@router.post("/upload/")
async def upload(file: UploadFile = File(...)):
    UPLOAD_DIR = "data"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract and chunk
    full_text = extract_text_from_file(file_path)
    chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]

    metadatas = [
        {
            "doc_id": file.filename,
            "chunk_id": i,
            "citation": f"Page {(i//5)+1}, Para {(i%5)+1}" # Example not actual logic
        }
        for i in range(len(chunks))
    ]

    add_to_vectorstore(chunks, metadatas)
    uploaded_files_set.add(file.filename)
    return {"filename": file.filename, "chunks": len(chunks)}



@router.post("/query/", response_model=QueryResponse)
async def query_route(query: str = Form(...), selected_docs: List[str] = Form(...)):
    top_chunks = query_vectorstore(query)

    filtered_chunks = [chunk for chunk in top_chunks if chunk["metadata"]["doc_id"] in selected_docs]
    # # Texts for LLaMA
    # contexts = [chunk["text"] for chunk in filtered_chunks]

    # LLaMA call with structured answer + themes
    result = get_answer_and_themes(query, filtered_chunks)

    # Generate mock individual answers for table (improve later with metadata)
    individual_answers = [
        DocumentAnswer(
            doc_id=chunk["metadata"].get("doc_id", f"DOC{i+1}"),
            answer=chunk["text"],
            citation=chunk["metadata"].get("citation", "Unknown")
        )
        for i, chunk in enumerate(top_chunks)
    ]

    # Convert dynamic theme results to Pydantic objects
    themes = [
        ThemeSummary(theme=t["theme"], supporting_docs=t["supporting_docs"])
        for t in result.get("themes", [])
    ]

    return QueryResponse(
        synthesized_answer=result.get("synthesized_answer", ""),
        individual_answers=individual_answers,
        themes=themes
    )
