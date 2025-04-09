# File: engine/pr.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def translate(strategic_thought: str, context: dict) -> str:
    user_question = context.get("user_question", "a business question")

    prompt = f"""
You are answering a business owner's question: "{user_question}"

Your job is to take a raw strategic idea and communicate it simply to your client, as if Elon Musk was explaining what matters most to them.

Here’s the raw strategy:
\"\"\"{strategic_thought}\"\"\"

Do not restate all the stats — focus on the mood, clarity, and message.
Be bold, but not buzzwordy. Keep it grounded and emotionally resonant.

Respond in 4 sentences or less.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content.strip()
    return result
