from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)


def get_synthesized_answer(query: str, contexts: list[str]) -> dict:
    """
    Generates a synthesized answer to the user's query by using the provided
    document excerpts as context.

    Parameters:
    - query (str): The user's input question or query.
    - contexts (list[str]): A list of relevant document excerpts (text chunks).

    Returns:
    - dict: A dictionary in the format { "synthesized_answer": "..." }
            containing the concise synthesized response from the model.
    """
    
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
    """
    Extracts key themes from the provided document excerpts in relation to the user's query.

    Parameters:
    - query (str): The user's input question or topic.
    - contexts (list[str]): A list of relevant document excerpts (text chunks).

    Returns:
    - dict: A dictionary in the following format:
        {
            "themes": [
                {
                    "theme": "string",
                    "individual_answers": "string",
                    "supporting_docs": ["DOC001"]
                }
            ]
        }
      Each theme represents a major idea, a supporting sentence, and the documents it came from.
    """
    
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
    return json.loads(response.choices[0].message.content)
