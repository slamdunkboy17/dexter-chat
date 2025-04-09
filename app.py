# File: app.py

import os
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from openai import OpenAI
from dotenv import load_dotenv

# 👉 Pull in your internal analysis logic
from engine.pipeline import run_pipeline

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Slack + Flask setup
slack_app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)
flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

# GPT-4 response logic
def generate_response(user_prompt):
    try:
        # Always try running pipeline, even if it returns empty
        context = run_pipeline(user_prompt)

        # Combine prompt + context for a richer reply, even if context is light
        full_prompt = (
            f"User question: {user_prompt}\n\n"
            f"Internal context:\n{context if context else '[No specific data found, use trends and analysis]'}"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Dexter, an AI growth assistant created by Winning Creative. "
                        "You're analytical, strategic, and speak confidently about marketing data and performance trends. "
                        "You respond based on a mix of internal campaign data, marketing strategy best practices, and observed trends. "
                        "Even when specific data isn't available, you provide sharp insight using your expertise."
                    )
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

# Respond to DMs
@slack_app.event("message")
def handle_message(event, say):
    channel_type = event.get("channel_type")
    text = event.get("text")

    if channel_type == "im" and not event.get("bot_id"):
        gpt_response = generate_response(text)
        say(gpt_response)

# Handle Slack challenge + events
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    payload = request.get_json()

    if payload.get("type") == "url_verification":
        return jsonify({"challenge": payload["challenge"]})

    return handler.handle(request)

# Run Flask app
if __name__ == "__main__":
    print("✅ Flask server running at http://localhost:3000")
    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port)
