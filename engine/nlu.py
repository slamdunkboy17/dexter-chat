# File: engine/nlu.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from utils.notion_utils import fetch_all_clients

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_slug_from_question(question: str, fallback_slug: str = "") -> str:
    """
    Broad-match slug detection using Notion client data.
    Returns best match or fallback slug if none found.
    """
    question_lower = question.lower()
    for client in fetch_all_clients():
        if client["name"] in question_lower:
            print(f"🔎 Detected client: {client['name']} → Slug: {client['slug']}")
            return client["slug"]
    print("⚠️ No match found, using fallback slug.")
    return fallback_slug


def parse(question, fallback_slug):
    """
    Uses GPT to extract intent and entities from a user question.
    Also detects the appropriate client slug from the question text.
    """
    resolved_slug = detect_slug_from_question(question, fallback_slug)

    prompt = f"""
    You're an intelligent assistant analyzing a marketing question.

    Given this user query: "{question}", return a JSON object with:
    - "intent": a short label for the type of question (e.g. "performance_review", "growth_strategy", "budget_optimization", etc.)
    - "entities": a list of any key terms, brands, or themes mentioned in the question
    - "slug": the company/client this applies to (use: "{resolved_slug}")

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
            "slug": resolved_slug,
            "raw": content  # Store original output in case of error
        }

    return parsed
