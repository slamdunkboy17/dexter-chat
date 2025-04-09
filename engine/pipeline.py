# File: engine/pipeline.py

from . import nlu, retrieve, math, trends, strategy, pr, polish
from utils.notion_utils import fetch_all_clients
import re

# Global cache of known clients
KNOWN_CLIENTS = fetch_all_clients()  # Returns list of {"name": ..., "slug": ...}
RECENT_SLUGS = {}  # user_id -> last used slug

def normalize_string(s: str) -> str:
    # Remove any non-alphanumeric characters and convert to lowercase.
    return re.sub(r'\W+', '', s.lower())

def match_slug_from_text(text: str) -> str:
    norm_text = normalize_string(text)
    for client in KNOWN_CLIENTS:
        norm_name = normalize_string(client["name"])
        norm_slug = normalize_string(client["slug"])
        # Check if either the normalized name or slug is in the normalized text.
        if norm_name in norm_text or norm_slug in norm_text:
            print(f"🔎 Matched client '{client['name']}' (slug: {client['slug']}) with input '{text}'")
            return client["slug"]
    return None

def analyze_for_question(slug: str, user_question: str, fallback: bool = False, user_id: str = None) -> str:
    """
    Main pipeline executor. If fallback=True, skips data retrieval and math,
    but still uses trends + strategy layers.
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
    else:
        # Safe defaults to avoid KeyErrors for references like lead_change/user_change
        metrics = {
            "total_cost": None,
            "total_conversions": None,
            "conversion_rate": None,
            "cpl": None,
            "benchmark_cpl": None,
            "lead_change": None,
            "user_change": None,
        }

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
    print(f"🔍 Matched slug from text: {slug}")


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
