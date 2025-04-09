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
    print("📎 Industry:", raw_data["industry"])
    print("📎 Benchmark CPL:", raw_data["benchmark_cpl"])
    print("📎 Ads rows:", len(raw_data["ads_df"]))
    print("📎 GA rows:", len(raw_data["ga_df"]))


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
