from openai import OpenAI
import json
from app.core.config import GROQ_API_KEY

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)


def get_synthesized_answer(query: str, contexts: list[str]) -> dict:
    context_text = "\n".join(f"- {c}" for c in contexts)
    prompt = f"""You are a document summarizer. 
    Given the excerpts below and the question, return a concise answer in JSON:
    {{ "synthesized_answer": "..." }}
    
    Excerpts:
    {context_text}
    Question: {query}
    """

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are an expert document summarizer."},
            {"role": "user", "content": prompt}
        ]
    )
    return json.loads(response.choices[0].message.content)


def get_themes(query: str, contexts: list[str]) -> dict:
    context_text = "\n".join(f"- {c}" for c in contexts)
    prompt = f"""You are a theme extractor. 
    Given the document excerpts, extract key themes and a sentence related to that theme and their supporting docs in JSON, only this no other text:
    
    {{
      "themes": [
        {{
          "theme": "string",
          "individual_answers": "string",
          "supporting_docs": ["DOC001"]
        }}
      ]
    }}
    
    Excerpts:
    {context_text}
    Question: {query}
    """
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are an expert theme extractor."},
            {"role": "user", "content": prompt}
        ]
    )
    print("LLM Output:", response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)
