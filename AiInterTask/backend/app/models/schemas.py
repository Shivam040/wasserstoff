from pydantic import BaseModel
from typing import List, Optional

class UploadResponse(BaseModel):
    filename: str
    chunks: int

class QueryRequest(BaseModel):
    query: str

class DocumentAnswer(BaseModel):
    doc_id: str
    answer: str
    citation: str  # e.g., "Page 4, Para 2"

class ThemeSummary(BaseModel):
    theme: str
    supporting_docs: List[str]  # e.g., ["DOC001", "DOC005"]

class QueryResponse(BaseModel):
    synthesized_answer: str
    individual_answers: List[DocumentAnswer]
    themes: Optional[List[ThemeSummary]] = None
