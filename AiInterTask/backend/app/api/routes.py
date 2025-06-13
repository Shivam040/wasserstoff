from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.extractor import extract_text_with_metadata
from app.services.embedder import add_to_vectorstore, query_vectorstore
from app.models.schemas import QueryResponse, DocumentAnswer, ThemeSummary
from app.services.groq_llm import get_synthesized_answer, get_themes
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

    # Extract with paragraph + page metadata
    extracted_paragraphs = extract_text_with_metadata(file_path)

    # Create text chunks and metadata
    chunks = [entry["text"] for entry in extracted_paragraphs]
    metadatas = [
        {
            "doc_id": file.filename,
            "chunk_id": i,
            "citation": f"Page {entry['page']}, Para {entry['para']}"
        }
        for i, entry in enumerate(extracted_paragraphs)
    ]

    add_to_vectorstore(chunks, metadatas)
    uploaded_files_set.add(file.filename)
    return {"filename": file.filename, "chunks": len(chunks)}



@router.post("/query/", response_model=QueryResponse)
async def query_route(query: str = Form(...), selected_docs: List[str] = Form(...)):
    # Step 1: Query vector DB
    top_chunks = query_vectorstore(query)

    # Step 2: Filter by selected documents
    filtered_chunks = [chunk for chunk in top_chunks if chunk["metadata"]["doc_id"] in selected_docs]

    # Step 3: Deduplicate by (doc_id, text, citation)
    seen = set()
    unique_chunks = []
    for chunk in filtered_chunks:
        kdoc_id = chunk["metadata"].get("doc_id", "")
        citation = chunk["metadata"].get("citation", "")

        key = (kdoc_id, citation)  # only remove if same doc + same citation

        if key not in seen:
            seen.add(key)
            unique_chunks.append(chunk)

    # Step 4: Prepare context for LLaMA
    contexts = [chunk["text"] for chunk in unique_chunks]
    result = get_synthesized_answer(query, contexts)
    themes_result = get_themes(query, contexts)

    # Step 5: Build document answers list
    individual_answers = [
        DocumentAnswer(
            doc_id=chunk["metadata"].get("doc_id", f"DOC{i+1}"),
            answer = chunk["text"],
            citation=chunk["metadata"].get("citation", f"Chunk {i}")
        )
        for i, chunk in enumerate(unique_chunks)
    ]

    # Step 6: Convert themes
    themes = [
        ThemeSummary(
            theme=t["theme"],
            description=t["individual_answers"],
            supporting_docs=list(set(t["supporting_docs"]))  # remove any duplicates here too
        )
        for t in themes_result.get("themes", [])
    ]

    return QueryResponse(
        synthesized_answer=result.get("synthesized_answer", ""),
        individual_answers=individual_answers,
        themes=themes
    )
