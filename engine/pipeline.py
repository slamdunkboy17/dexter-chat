# File: engine/pipeline.py

from . import nlu, retrieve, math, trends, strategy, pr, polish
from utils.notion_utils import fetch_all_clients
import re

# Global cache of known clients
KNOWN_CLIENTS = fetch_all_clients()  # Returns list of {"name": ..., "slug": ...}
RECENT_SLUGS = {}  # user_id -> last used slug

def match_slug_from_text(text):
    """
    Attempt to find a client slug by matching their name or slug in the question.
    """
    text = text.lower()
    for client in KNOWN_CLIENTS:
        name = client["name"]
        slug = client["slug"]
        if name in text or slug in text:
            return slug
    return None

def analyze_for_question(slug: str, user_question: str, fallback: bool = False, user_id: str = None) -> str:
    """
    Main pipeline executor. If fallback=True, skips data and only uses trends and strategy.
    """
    print("🧠 Starting NLU layer...")
    question_context = nlu.parse(user_question, slug)
    if user_id:
        question_context["user_id"] = user_id
    print("📎 NLU Output:", question_context)

    metrics = {}
    raw_data = {}

    if not fallback:
        print("📥 Retrieving data...")
        raw_data = retrieve.collect(slug)
        print("📊 Raw data retrieved for", slug)
        print("📎 Industry:", raw_data.get('industry'))
        print("📎 Benchmark CPL:", raw_data.get('benchmark_cpl'))
        print("📎 Ads rows:", len(raw_data.get("ads_df", [])))
        print("📎 GA rows:", len(raw_data.get("ga_df", [])))

        print("🧮 Calculating performance metrics...")
        metrics = math.calculate(raw_data)

    print("🌐 Gathering market trends...")
    industry = raw_data.get("industry", "general marketing")
    industry_trends = trends.get_trends(industry)

    print("🧠 Generating strategic insight...")
    strategic_thought = strategy.generate(metrics, industry_trends, question_context)

    print("🪄 Translating into PR narrative...")
    narrative = pr.translate(strategic_thought, question_context)

    print("🧽 Final polishing for clarity and format...")
    final_message = polish.refine(narrative, metrics, question_context)

    print("✅ Pipeline complete.")
    return final_message

def run_pipeline(user_question: str, user_id: str = None) -> str:
    """
    External entry point to run the pipeline with dynamic slug detection and fallback support.
    """
    slug = match_slug_from_text(user_question)

    if not slug and user_id:
        slug = RECENT_SLUGS.get(user_id)

    fallback_mode = False

    if slug:
        if user_id:
            RECENT_SLUGS[user_id] = slug
    else:
        fallback_mode = True
        slug = "general"  # Not used to fetch data, just passed to NLU

    return analyze_for_question(slug, user_question, fallback=fallback_mode, user_id=user_id)
