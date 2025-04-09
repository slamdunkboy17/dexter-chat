# File: engine/strategy.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate(metrics, trends, question_context):
    industry = question_context.get("industry", "Unknown Industry")
    intent = question_context.get("intent", "general_growth")
    slug = question_context.get("slug", "the company")

    # ✅ Safely format percentage deltas
    lead_delta_str = f"{metrics['lead_change']:+.1f}%" if metrics['lead_change'] is not None else "N/A"
    user_delta_str = f"{metrics['user_change']:+.1f}%" if metrics['user_change'] is not None else "N/A"

    prompt = f"""
You are a creative growth strategist inspired by Steve Jobs and Virgil Abloh.

You are advising a business called "{slug}" in the **{industry}** industry.
Your goal is to translate numbers and trends into a bold but realistic 3–6 month growth idea.

Here are some key performance insights:
- Ad Spend: ${metrics['total_cost']:.2f}
- Conversions: {int(metrics['total_conversions'])}
- Conversion Rate: {metrics['conversion_rate']:.2f}%
- CPL: ${metrics['cpl']:.2f}
- Benchmark CPL: ${metrics['benchmark_cpl']}
- Leads vs. previous period: {lead_delta_str}
- GA Users vs. previous period: {user_delta_str}

Market Trends for this industry:
{trends}

User asked something related to: "{intent}"

Please return one strategic insight that:
- Synthesizes the data and current marketing trends
- Focuses on practical moves the business can take in the next 3–6 months
- Relates to performance marketing (Google Ads, SEO, content, email, etc.)
- Is creative, thoughtful, and high-leverage — not generic or obvious
- Is contextually relevant to the performance of the brand relative to the market
- Fixes something that needs to be fixed
- Don't emphasize AI or AI related topics

Respond with a single paragraph — no greetings, no summaries.
"""


    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content.strip()
    return result
