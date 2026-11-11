import sqlite3
import json

conn = sqlite3.connect("spiritual_places.db")
cursor = conn.cursor()

# Ensure landmark column exists
try:
    cursor.execute("ALTER TABLE places ADD COLUMN landmark TEXT")
except sqlite3.OperationalError:
    pass # Column already exists

sample_places = [
    {
        "name": "Tirupati Sri Venkateswara Swamy Temple",
        "category": "Temples",
        "landmark": "Near Seshachalam Seven Hills & Pushkarini Lake",
        "location": "Tirumala, Tirupati, Andhra Pradesh",
        "address": "S Mada St, Tirumala, Tirupati, Andhra Pradesh 517504",
        "description": "Ancient temple dedicated to Lord Venkateswara located atop the seven peaks of Seshachalam Hills.",
        "map_embed": "https://maps.google.com/maps?q=Tirupati+Venkateswara+Temple+Tirumala&t=&z=15&ie=UTF8&iwloc=&output=embed",
        "gallery": ["kashi.jpg"]
    },
    {
        "name": "Sri Bhramaramba Mallikarjuna Temple",
        "category": "Temples",
        "landmark": "Near Krishna River & Nallamala Forest Range",
        "location": "Srisailam, Andhra Pradesh",
        "address": "Srisailam, Nandyal District, Andhra Pradesh 518101",
        "description": "One of the 12 sacred Jyotirlingas of Lord Shiva situated high on the Nallamala Hills.",
        "map_embed": "https://maps.google.com/maps?q=Srisailam+Mallikarjuna+Temple&t=&z=15&ie=UTF8&iwloc=&output=embed",
        "gallery": ["kashi.jpg"]
    }
]

for p in sample_places:
    cursor.execute("""
        INSERT INTO places (name, category, landmark, location, address, description, map_embed, gallery)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p["name"], p["category"], p["landmark"], p["location"],
        p["address"], p["description"], p["map_embed"], json.dumps(p["gallery"])
    ))

conn.commit()
conn.close()
print("Database updated with landmark details!")