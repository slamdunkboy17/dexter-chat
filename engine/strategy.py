# File: engine/strategy.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate(metrics, trends, question_context):
    industry = question_context.get("industry", "Unknown Industry")
    intent = question_context.get("intent", "general_growth")
    slug = question_context.get("slug", "the company")

    # -- Safely format numeric metrics (avoid .2f on None) --

    # Ad Spend
    total_cost = metrics.get("total_cost")
    total_cost_str = f"{float(total_cost):.2f}" if total_cost is not None else "N/A"

    # Conversions
    total_conversions = metrics.get("total_conversions")
    conversions_str = str(int(total_conversions)) if total_conversions is not None else "N/A"

    # Conversion Rate
    conversion_rate = metrics.get("conversion_rate")
    conv_rate_str = f"{float(conversion_rate):.2f}%" if conversion_rate is not None else "N/A"

    # CPL
    cpl = metrics.get("cpl")
    cpl_str = f"{float(cpl):.2f}" if cpl is not None else "N/A"

    # Benchmark CPL
    bench_cpl = metrics.get("benchmark_cpl")
    bench_cpl_str = f"{float(bench_cpl):.2f}" if bench_cpl is not None else "N/A"

    # Lead change
    lead_change = metrics.get("lead_change")
    lead_delta_str = f"{lead_change:+.1f}%" if lead_change is not None else "N/A"

    # User change
    user_change = metrics.get("user_change")
    user_delta_str = f"{user_change:+.1f}%" if user_change is not None else "N/A"

    prompt = f"""
You are a creative growth strategist inspired by Steve Jobs and Virgil Abloh.

You are advising a business called "{slug}" in the **{industry}** industry.
Your goal is to translate numbers and trends into a bold but realistic 3–6 month growth idea.

Here are some key performance insights:
- Ad Spend: ${total_cost_str}
- Conversions: {conversions_str}
- Conversion Rate: {conv_rate_str}
- CPL: ${cpl_str}
- Benchmark CPL: ${bench_cpl_str}
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
