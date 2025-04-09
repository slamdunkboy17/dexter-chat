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
            try:
                props = result["properties"]
                name_raw = props.get("Client", {}).get("title", [])
                slug_raw = props.get("Slug", {}).get("rich_text", [])

                name = name_raw[0]["plain_text"].strip() if name_raw else None
                slug = slug_raw[0]["plain_text"].strip() if slug_raw else None

                if not name or not slug:
                    print(f"⚠️ Missing or invalid Name/Slug in result: {result['id']}")
                    continue

                all_clients.append({"name": name.lower(), "slug": slug.lower()})

            except Exception as e:
                print("⚠️ Error parsing Notion client row:", e)

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)

    print(f"✅ Loaded {len(all_clients)} clients from Notion.")
    print("Clients:", all_clients)
    return all_clients
