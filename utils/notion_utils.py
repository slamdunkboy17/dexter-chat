import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_client_properties_from_notion(slug):
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    
    payload = {
        "filter": {
            "property": "Slug",
            "rich_text": {
                "equals": slug
            }
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print("⚠️ Notion query failed:", response.status_code, response.text)
        return {}

    results = response.json().get("results")
    if not results:
        print("⚠️ No Notion results for slug:", slug)
        return {}

    props_raw = results[0]["properties"]

    # Normalize and extract properties
    props = {}
    for key, val in props_raw.items():
        norm_key = key.strip().lower().replace(" ", "_")

        if val["type"] == "select":
            props[norm_key] = val["select"]["name"] if val["select"] else None
        elif val["type"] == "number":
            props[norm_key] = val["number"]
        elif val["type"] == "rich_text":
            props[norm_key] = val["rich_text"][0]["plain_text"] if val["rich_text"] else None
        elif val["type"] == "title":
            props[norm_key] = val["title"][0]["plain_text"] if val["title"] else None

    print("✅ Parsed Notion properties:", props)
    return props
