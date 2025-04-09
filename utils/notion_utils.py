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
    """Fetch properties for a specific client by slug."""
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
    props = {}

    for key, val in props_raw.items():
        norm_key = key.strip().lower().replace(" ", "_")

        try:
            if val["type"] == "select":
                props[norm_key] = val["select"]["name"] if val["select"] else None
            elif val["type"] == "number":
                props[norm_key] = val["number"]
            elif val["type"] == "rich_text":
                props[norm_key] = val["rich_text"][0]["plain_text"] if val["rich_text"] else None
            elif val["type"] == "title":
                props[norm_key] = val["title"][0]["plain_text"] if val["title"] else None
        except Exception as e:
            print(f"⚠️ Error parsing property {key}: {e}")

    print("✅ Parsed Notion properties:", props)
    return props


def fetch_all_clients():
    """Pulls all client names and slugs from Notion for use in fuzzy/broad match."""
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    
    all_clients = []
    has_more = True
    next_cursor = None

    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code != 200:
            print("⚠️ Failed to fetch all clients from Notion:", response.status_code)
            return []

        data = response.json()
        for result in data.get("results", []):
            props = result.get("properties", {})
            name_field = props.get("Name")
            slug_field = props.get("Slug")

            # Defensive: check presence and type
            if not name_field or name_field["type"] != "title" or not name_field["title"]:
                print(f"⚠️ Missing or invalid Name in result: {result.get('id')}")
                continue
            if not slug_field or slug_field["type"] != "rich_text" or not slug_field["rich_text"]:
                print(f"⚠️ Missing or invalid Slug in result: {result.get('id')}")
                continue

            name = name_field["title"][0]["plain_text"].strip().lower()
            slug = slug_field["rich_text"][0]["plain_text"].strip().lower()

            all_clients.append({"name": name, "slug": slug})

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    print(f"✅ Loaded {len(all_clients)} clients from Notion.")
    print("Clients:", all_clients)
    return all_clients
