import requests
import json

url = "https://dp4p6x0xfi5o9.cloudfront.net/maimai/data.json"

try:
    resp = requests.get(url)
    resp.raise_for_status()           # → raises if HTTP status is 4xx/5xx
    data = resp.json()                # → parses JSON into dict/list
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
    data = None
except ValueError:
    print("Response wasn’t valid JSON")
    data = None

if data is not None:
    with open("songs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

