# File: engine/nlu.py

import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse(question, slug):
    """
    Uses GPT to extract intent and entities from a user question.
    """
    prompt = f"""
    You're an intelligent assistant analyzing a marketing question.

    Given this user query: "{question}", return a JSON object with:
    - "intent": a short label for the type of question (e.g. "performance_review", "growth_strategy", "budget_optimization", etc.)
    - "entities": a list of any key terms, brands, or themes mentioned in the question
    - "slug": the company/client this applies to (use: "{slug}")

    Only respond with valid JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {
            "intent": "unknown",
            "entities": [],
            "slug": slug,
            "raw": content  # Store original output in case of error
        }

    return parsed
