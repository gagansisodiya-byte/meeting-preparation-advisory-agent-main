import os

from dotenv import load_dotenv
from openai import OpenAI


def _create_client() -> OpenAI:
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to data/.env before requesting AI advice."
        )

    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def generate_ai_advice(
    topic: str,
    updates: str,
    pending_tasks: str,
    notes: str,
) -> str:
    prompt = f"""
You are a Meeting Preparation Advisory Agent.

Prepare a useful meeting brief using the information below.

Meeting topic: {topic}
Project updates: {updates}
Pending tasks: {pending_tasks}
Relevant meeting notes: {notes}

Include:
1. Meeting summary
2. Key discussion points
3. Risks or blockers
4. Suggested questions
5. Recommended next actions

Do not invent facts. If information is missing, mention it.
"""

    response = _create_client().chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful meeting preparation assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    advice = response.choices[0].message.content
    if advice is None:
        raise RuntimeError("The AI provider returned an empty response.")
    return advice