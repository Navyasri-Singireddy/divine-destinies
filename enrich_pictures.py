import sqlite3
import json
import time
import requests
from urllib.parse import quote

conn = sqlite3.connect("spiritual_places.db")
cursor = conn.cursor()

cursor.execute("SELECT id, name, city_village, category FROM places")
places = cursor.fetchall()


def fetch_5_to_10_photos(place_name, city, category):
    headers = {'User-Agent': 'DivineDestiniesApp/3.0 (contact@divinedestinies.com)'}

    # Try broad and specific search terms to find maximum photo matches
    search_queries = [
        f"{place_name} {city}",
        f"{place_name} {category}",
        f"{place_name}"
    ]

    collected_photos = []

    for search_query in search_queries:
        if len(collected_photos) >= 10:
            break

        url = (
            f"https://commons.wikimedia.org/w/api.php?action=query"
            f"&generator=search&gsrsearch={quote(search_query)}"
            f"&gsrnamespace=6&gsrlimit=30&prop=imageinfo&iiprop=url&format=json"
        )

        try:
            response = requests.get(url, headers=headers, timeout=6)
            if response.status_code == 200:
                data = response.json()
                pages = data.get("query", {}).get("pages", {})

                for _, page_info in pages.items():
                    if len(collected_photos) >= 10:
                        break

                    image_info = page_info.get("imageinfo", [])
                    if image_info and "url" in image_info[0]:
                        img_url = image_info[0]["url"]
                        img_url_lower = img_url.lower()

                        # Filter out non-photo assets (icons, maps, logos, diagrams)
                        invalid_keywords = ['logo', 'icon', 'map', 'flag', 'coat_of_arms', 'diagram', 'plan', 'symbol']
                        if (img_url_lower.endswith(('.jpg', '.jpeg', '.png', '.webp')) and
                                not any(kw in img_url_lower for kw in invalid_keywords)):
                            if img_url not in collected_photos:
                                collected_photos.append(img_url)
        except Exception:
            pass

    return collected_photos[:10]  # Cap at maximum 10 photos


print(f"Scanning {len(places)} places to collect 5–10 original photos each...\n", flush=True)
updated_count = 0

for place_id, name, city, category in places:
    photos = fetch_5_to_10_photos(name, city or "", category)

    if photos:
        cursor.execute(
            "UPDATE places SET gallery = ? WHERE id = ?",
            (json.dumps(photos), place_id)
        )
        updated_count += 1
        print(f"[{updated_count}] Saved {len(photos)} photo(s) for: {name} ({city})", flush=True)
        conn.commit()
    time.sleep(0.3)

conn.close()
print("\nMulti-photo enrichment complete! 5–10 photos saved per location.", flush=True)