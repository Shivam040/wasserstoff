from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.extractor import extract_text_with_metadata
from app.services.embedder import add_to_vectorstore, query_vectorstore
from app.models.schemas import QueryResponse, DocumentAnswer, ThemeSummary
from app.services.groq_llm import get_synthesized_answer, get_themes
import os

# File Upload Route
router = APIRouter()
uploaded_files_set = set()

# Defines an POST API endpoint at /upload/, it expects a file to be uploaded via multipart form-data.

Expects a file to be uploaded via multipart form-data.
@router.post("/upload/")
async def upload(file: UploadFile = File(...)):
    # Creates the directory if it doesn't exist.
    UPLOAD_DIR = "data"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract with paragraph + page metadata
    extracted_paragraphs = extract_text_with_metadata(file_path)

    # Create text chunks and metadata
    chunks = [entry["text"] for entry in extracted_paragraphs]
    # Constructs metadata for each chunk including document name, chunk ID, and citation info.
    metadatas = [
        {
            "doc_id": file.filename,
            "chunk_id": i,
            "citation": f"Page {entry['page']}, Para {entry['para']}"
        }
        for i, entry in enumerate(extracted_paragraphs)
    ]
    # Adds the text chunks and their metadata into the vector store for future retrieval.
    add_to_vectorstore(chunks, metadatas)
    uploaded_files_set.add(file.filename)
    # Adds the file name to the set of uploaded files and returns a success response.
    return {"filename": file.filename, "chunks": len(chunks)}


# Defines a POST endpoint at /query/ it accepts two form parameters: query: user’s natural language query.
# and selected_docs: list of document IDs to restrict the search scope.
@router.post("/query/", response_model=QueryResponse)
async def query_route(query: str = Form(...), selected_docs: List[str] = Form(...)):
    # Queries the vector store using the input query and returns the most relevant text chunks.
    top_chunks = query_vectorstore(query)

    # Filters the top chunks to include only those that belong to the selected documents.
    filtered_chunks = [chunk for chunk in top_chunks if chunk["metadata"]["doc_id"] in selected_docs]

    # Deduplicates chunks based on (doc_id, citation) to avoid repeated content from same doc and position.
    seen = set()
    unique_chunks = []
    for chunk in filtered_chunks:
        kdoc_id = chunk["metadata"].get("doc_id", "")
        citation = chunk["metadata"].get("citation", "")

        key = (kdoc_id, citation)  # only remove if same doc + same citation

        if key not in seen:
            seen.add(key)
            unique_chunks.append(chunk)

    # Extracts texts from the unique chunks.
    contexts = [chunk["text"] for chunk in unique_chunks]
    # Gets a single synthesized answer and themes from the LLM using that context.
    result = get_synthesized_answer(query, contexts)
    themes_result = get_themes(query, contexts)

    # Prepares a list of answers, one per document chunk, with their citation info.
    individual_answers = [
        DocumentAnswer(
            doc_id=chunk["metadata"].get("doc_id", f"DOC{i+1}"),
            answer = chunk["text"],
            citation=chunk["metadata"].get("citation", f"Chunk {i}")
        )
        for i, chunk in enumerate(unique_chunks)
    ]

    # Formats each theme returned by the LLM and removes duplicate supporting documents.
    themes = [
        ThemeSummary(
            theme=t["theme"],
            description=t["individual_answers"],
            supporting_docs=list(set(t["supporting_docs"])) 
        )
        for t in themes_result.get("themes", [])
    ]

    # Constructs and returns the complete response in a structured schema.
    return QueryResponse(
        synthesized_answer=result.get("synthesized_answer", ""),
        individual_answers=individual_answers,
        themes=themes
    )
