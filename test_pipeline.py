# File: test_pipeline.py

from engine.pipeline import analyze_for_question

if __name__ == "__main__":
    slug = "hproofing"
    question = "What kind of Google Ads support does HP Roofing need right now?"
    
    print("⏳ Running Dexter pipeline...\n")
    response = analyze_for_question(slug, question)
    
    print("\n📬 Final Output:\n")
    print(response)
