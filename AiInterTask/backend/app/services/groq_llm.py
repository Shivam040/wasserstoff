from openai import OpenAI
from app.core.config import GROQ_API_KEY

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

def get_answer_from_llama(query: str, contexts: list[str]) -> str:
    context_text = "\n".join(f"- {c}" for c in contexts)

    prompt = f"""Answer the question based on the following document excerpts.
            Context:
            {context_text}

            Question: {query}

            Return a well-structured answer and mention document snippets that support the answer.
            """

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are an expert document assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
