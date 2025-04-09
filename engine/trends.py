# File: engine/trends.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_trends(industry: str) -> str:
    prompt = f"""
Act as a marketing trend analyst.

In 3 sentences, summarize the current major trends and strategies in the **{industry}** industry — especially related to advertising, SEO, social media, or lead generation.

Avoid generalities — be specific and timely (think Q2 2025). Mention tools, tactics, and changes in consumer behavior if relevant.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
