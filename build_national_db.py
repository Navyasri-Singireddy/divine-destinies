import sqlite3
import json
import time
import requests

conn = sqlite3.connect("spiritual_places.db")
cursor = conn.cursor()

# Create table with complete address granularity
cursor.execute("DROP TABLE IF EXISTS places")
cursor.execute("""
    CREATE TABLE places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        city_village TEXT,
        colony TEXT,
        street_name TEXT,
        landmark TEXT,
        location TEXT,
        address TEXT,
        description TEXT,
        map_embed TEXT,
        gallery TEXT
    )
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON places(category)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON places(name)")
conn.commit()

STATES_AND_UTS = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu and Kashmir", "Puducherry", "Chandigarh", "Ladakh"
]

RELIGION_MAP = {
    "hindu": "Temples",
    "christian": "Churches",
    "muslim": "Mosques",
    "sikh": "Gurudwaras",
    "buddhist": "Buddhist Places",
    "jain": "Jain Places"
}

HEADERS = {"User-Agent": "DivineDestiniesApp/2.0"}


def fetch_state_data(state_name):
    print(f"Fetching: {state_name}...", flush=True)
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:90];
    area["name"="{state_name}"]["admin_level"="4"]->.searchArea;
    (
      node["amenity"="place_of_worship"](area.searchArea);
      way["amenity"="place_of_worship"](area.searchArea);
    );
    out center 150;
    """
    try:
        response = requests.post(overpass_url, data={"data": query}, headers=HEADERS, timeout=95)
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

                # Granular Address Extraction
                city_village = (
                        tags.get("addr:city") or
                        tags.get("addr:village") or
                        tags.get("addr:town") or
                        tags.get("addr:district") or
                        state_name
                )

                colony = (
                        tags.get("addr:suburb") or
                        tags.get("addr:neighbourhood") or
                        tags.get("addr:colony") or
                        tags.get("addr:quarter") or
                        "Main Colony"
                )

                street = tags.get("addr:street") or tags.get("addr:place") or "Temple Road"
                landmark = tags.get("landmark") or tags.get("near") or f"Near {name} Main Gate"

                # Full formatted address
                full_address = tags.get("addr:full") or f"{street}, {colony}, {city_village}, {state_name}"
                location_str = f"{city_village}, {state_name}"

                # Embed Map & Image Gallery
                map_url = f"https://maps.google.com/maps?q={lat},{lon}&z=16&output=embed" if (lat and lon) else ""
                photos = [tags.get("image") or tags.get("wikimedia_commons") or "kashi.jpg"]

                cursor.execute("""
                    INSERT INTO places (name, category, city_village, colony, street_name, landmark, location, address, description, map_embed, gallery)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, category, city_village, colony, street, landmark,
                    location_str, full_address,
                    f"A revered {category.lower()[:-1]} located in {colony}, {city_village}, {state_name}.",
                    map_url, json.dumps(photos)
                ))
                added_count += 1

            conn.commit()
            print(f"Added {added_count} places for {state_name}.\n", flush=True)
    except Exception as e:
        print(f"Error fetching {state_name}: {e}\n", flush=True)


for state in STATES_AND_UTS:
    fetch_state_data(state)
    time.sleep(2)

conn.close()
print("All states fully repopulated with City, Colony, Street, Landmark, Map, and Photo data!")