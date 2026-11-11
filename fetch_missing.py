import sqlite3
import json
import time
import requests

MISSING_STATES = [
    "Himachal Pradesh",
    "Meghalaya",
    "Chhattisgarh",
    "Karnataka",
    "Maharashtra",
    "Sikkim",
    "Telangana",
    "Jammu and Kashmir",
    "Chandigarh",
]

# Multiple global Overpass API mirrors for automatic fallback
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.ai/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

RELIGION_MAP = {
    "hindu": "Temples",
    "christian": "Churches",
    "muslim": "Mosques",
    "sikh": "Gurudwaras",
    "buddhist": "Buddhist Places",
    "jain": "Jain Places"
}

HEADERS = {"User-Agent": "SpiritualPlacesApp/2.0 (contact: support@divinedestinies.com)"}

conn = sqlite3.connect("spiritual_places.db")
cursor = conn.cursor()


def fetch_single_state(state_name):
    print(f"\nFetching: {state_name}...", flush=True)
    query = f"""
    [out:json][timeout:60];
    area["name"="{state_name}"]["admin_level"="4"]->.searchArea;
    (
      node["amenity"="place_of_worship"](area.searchArea);
      way["amenity"="place_of_worship"](area.searchArea);
    );
    out center 100;
    """

    success = False
    for server_url in OVERPASS_SERVERS:
        print(f" -> Trying mirror: {server_url}...", flush=True)
        try:
            response = requests.post(server_url, data={"data": query}, headers=HEADERS, timeout=45)
            if response.status_code == 200:
                elements = response.json().get("elements", [])
                added_count = 0
                for item in elements:
                    tags = item.get("tags", {})
                    name = tags.get("name") or tags.get("name:en")
                    religion_raw = tags.get("religion", "").lower()

                    if not name or religion_raw not in RELIGION_MAP:
                        continue

                    category = RELIGION_MAP[religion_raw]
                    lat = item.get("lat") or item.get("center", {}).get("lat")
                    lon = item.get("lon") or item.get("center", {}).get("lon")

                    city_village = (
                            tags.get("addr:city") or
                            tags.get("addr:village") or
                            tags.get("addr:town") or
                            state_name
                    )
                    colony = tags.get("addr:suburb") or tags.get("addr:neighbourhood") or "Main Area"
                    street = tags.get("addr:street") or "Temple Road"
                    landmark = tags.get("landmark") or f"Near {name}"
                    full_address = tags.get("addr:full") or f"{street}, {colony}, {city_village}, {state_name}"

                    map_url = f"https://maps.google.com/maps?q={lat},{lon}&z=16&output=embed" if (lat and lon) else ""

                    cursor.execute("""
                        INSERT INTO places (name, category, city_village, colony, street_name, landmark, location, address, description, map_embed, gallery)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        name, category, city_village, colony, street, landmark,
                        f"{city_village}, {state_name}", full_address,
                        f"A revered {category.lower()[:-1]} located in {city_village}, {state_name}.",
                        map_url, json.dumps(["kashi.jpg"])
                    ))
                    added_count += 1

                conn.commit()
                print(f" SUCCESS: Added {added_count} places for {state_name}.", flush=True)
                success = True
                break
        except Exception as e:
            print(f"    Mirror failed/timed out. Switching to next mirror...", flush=True)
            time.sleep(2)

    if not success:
        print(f" FAILED: Could not reach any mirror for {state_name}.", flush=True)


for state in MISSING_STATES:
    fetch_single_state(state)
    time.sleep(4)

conn.close()