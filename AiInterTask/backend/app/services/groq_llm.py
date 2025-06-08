from openai import OpenAI
import json
from app.core.config import GROQ_API_KEY

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

def get_answer_and_themes(query: str, contexts: list[str]) -> dict:
    context_text = "\n".join(f"- {c}" for c in contexts)

    prompt = f"""You are a legal document assistant.

            Given the following document excerpts and the user's question, do two things:

            1. Provide a well-structured answer to the question.
            2. Identify and list any common themes across these document excerpts. For each theme, include a list of supporting document IDs or descriptions.

            Document Excerpts:
            {context_text}

            Question: {query}

            Return your response in JSON format like this:
            {{
            "synthesized_answer": "...",
            "themes": [
                {{
                "theme": "Theme description here",
                "supporting_docs": ["DOC001", "DOC002"]
                }},
                ...
            ]
            }}
            """

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are an expert document summarizer."},
            {"role": "user", "content": prompt}
        ]
    )

    # Parse string to dict
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except Exception as e:
        print("LLM returned invalid JSON:", content)
        return {"synthesized_answer": content, "themes": []}

