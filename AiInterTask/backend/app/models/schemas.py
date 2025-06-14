from pydantic import BaseModel
from typing import List, Optional

# This model is used to represent the response after uploading a file.
class UploadResponse(BaseModel):
    filename: str
    chunks: int
    
# Represents the body of a query request i.e. The user’s input string asking a question.
class QueryRequest(BaseModel):
    query: str

# Represents a text snippet from a document that is relevant to the query.
class DocumentAnswer(BaseModel):
    doc_id: str
    answer: str    # The chunk of relevant text.
    citation: str  # e.g., "Page 4, Para 2"

# Represents a theme derived from relevant text chunks.
class ThemeSummary(BaseModel):
    theme: str
    description: str
    supporting_docs: List[str]  # e.g., ["DOC001", "DOC005"]

# Represents the response to a user query.
class QueryResponse(BaseModel):
    synthesized_answer: str
    individual_answers: List[DocumentAnswer]
    themes: Optional[List[ThemeSummary]] = None
