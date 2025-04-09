# File: engine/pipeline.py

from . import nlu, retrieve, math, trends, strategy, pr, polish

def analyze_for_question(slug: str, user_question: str) -> str:
    """
    Orchestrates Dexter's multi-layer intelligence pipeline to respond to a user question.
    """

    print("🧠 Starting NLU layer...")
    question_context = nlu.parse(user_question, slug)
    print("📎 NLU Output:", question_context)

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
    industry_trends = trends.get_trends(raw_data["industry"])

    print("🧠 Generating strategic insight...")
    strategic_thought = strategy.generate(metrics, industry_trends, question_context)

    print("🪄 Translating into PR narrative...")
    narrative = pr.translate(strategic_thought, question_context)

    print("🧽 Final polishing for clarity and format...")
    final_message = polish.refine(narrative, metrics, question_context)

    print("✅ Pipeline complete.")
    return final_message

def run_pipeline(user_question: str) -> str:
    """
    Default external pipeline interface that uses keyword matching to determine the client slug.
    """

    # 🔍 You can replace this with a more sophisticated slug detection if needed
    slug_map = {
        "hp roofing": "hp-roofing",
        "weathercheck": "weathercheck",
        "valor": "valor-exterior-partners",
    }

    lower_q = user_question.lower()
    slug = next((slug for key, slug in slug_map.items() if key in lower_q), None)

    if not slug:
        print("❗️No known client found in question. Skipping data-driven response.")
        return ""

    return analyze_for_question(slug, user_question)
