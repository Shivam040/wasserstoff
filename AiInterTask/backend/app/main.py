from fastapi import FastAPI
from AiInterTask.backend.app.services.embedder import query_vectorstore
from AiInterTask.backend.app.services.groq_llm import get_answer_from_llama
from app.api.routes import router
from app.models.schemas import QueryRequest, QueryResponse, DocumentAnswer, ThemeSummary
from fastapi import APIRouter
from fastapi import Form

app = FastAPI()
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}


@router.post("/query/", response_model=QueryResponse)
async def query_endpoint(query: str = Form(...)):
    contexts = query_vectorstore(query)
    llm_answer = get_answer_from_llama(query, contexts)

    # Dummy example output
    doc_answers = [
        DocumentAnswer(doc_id="DOC001", answer="It states penalties...", citation="Page 2, Para 1"),
        DocumentAnswer(doc_id="DOC002", answer="Clause 49 violation...", citation="Page 3, Para 2")
    ]

    themes = [
        ThemeSummary(theme="Regulatory Non-Compliance", supporting_docs=["DOC001", "DOC002"])
    ]

    return QueryResponse(
        synthesized_answer=llm_answer,
        individual_answers=doc_answers,
        themes=themes
    )
