# Gen-AI Document Theme Identifier Chatbot

A full-stack Gen-AI-powered web application that allows users to upload documents (PDFs, images, or text), ask contextual questions, and receive synthesized answers and thematic insights using LLMs and vector search.

## Features
- Can process 75+ documents (PDF/text/image with OCR)
- Upload `.pdf`, `.txt`, or image files (`.jpg`, `.png`, `.jpeg`)
- Store & manage document for fast search
- Query: can ask in natural language
- Extracts synthesized answers (doc_id, text, citation) and themes across documents
- Letting users include/exclude specific document from search

---

## 🔁 Workflow

### 1. Document Ingestion
- Users upload PDFs/images via Streamlit frontend
- Backend handles:
  - OCR using `pytesseract` (for scanned docs)
  - PDF parsing using `PyMuPDF`

### 2. Text Preprocessing & Chunking
- Extracted text is cleaned and split into paragraphs with:
  - `document_name`
  - `page_number`
  - `para_number`

### 3. Vectorization & Storage
- Paragraphs are embedded using `all-MiniLM-L6-v2` (Sentence Transformers)
- Stored in `ChromaDB` for similarity search
- Duplicate entries are removed based on document, page, and paragraph number

### 4. Query Handling
- User query is embedded and matched against vector DB
- Top-k relevant paragraphs are retrieved

### 5. LLM Answer Synthesis
- Retrieved context + query is sent to Groq's LLaMA 3-70B
- LLM returns:
  - `answer` – synthesized response
  - `evidence` – supporting text
  - `themes` – high-level issues like "Battery Constraints", "Policy Gaps"

### 6. Theme Extraction
- Themes are extracted and structured from LLM output
- Includes policy issues, hardware constraints, and operational gaps

### 7. UI Rendering
- Chat interface for query input and output
- Displays answer, evidence, and identified themes
- Document upload panel on sidebar

---

---
## Project Structure

wasserstoff/
├── AiInterTask/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                  # FastAPI entrypoint
│   │   │   ├── api/
│   │   │   │   └── routes.py            # API endpoints
│   │   │   ├── models/
│   │   │   │   └── schemas.py           # Pydantic models
│   │   │   ├── services/
│   │   │   │   ├── extractor.py         # Text extraction (PDF, OCR, TXT)
│   │   │   │   ├── embedder.py          # ChromaDB setup, vector search
│   │   │   │   └── groq_llm.py          # LLaMA3-based LLM interactions
│   │   ├── Dockerfile                   # Docker config for backend
│   │   └── requirements.txt
│   │
│   ├── frontend/
│   │   ├── app.py                       # Streamlit frontend
│   │   └── requirements.txt
│
├── docker-compose.yml                  # Compose for frontend + backend
├── .env                                # Environment variables
└── README.md                           # ← (This file)


## Running the Project

### Docker Compose (Recommended)

```bash
docker-compose up --build
```

##  Example Use Case
Upload 3 PDF reports. Ask:
"What are the key challenges in electric mobility?"

 ## Powered By:
- Groq LLaMA3-70B
- ChromaDB
- Sentence-Transformers
- PDFPlumber
- pytesseract
- FastAPI
- Streamlit

## Author
Built with ❤️ by Shivam Dangwal
