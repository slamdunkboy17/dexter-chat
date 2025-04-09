# File: app.py

import os
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from openai import OpenAI
from dotenv import load_dotenv

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
def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
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

    # Slack URL verification
    if payload.get("type") == "url_verification":
        return jsonify({"challenge": payload["challenge"]})

    # Forward event to Slack Bolt
    return handler.handle(request)

# Run Flask app
if __name__ == "__main__":
    print("✅ Flask server running at http://localhost:3000")
    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port)
