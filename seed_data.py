import sqlite3
import json

conn = sqlite3.connect("spiritual_places.db")
cursor = conn.cursor()

# Drop existing table so new columns build correctly
cursor.execute("DROP TABLE IF EXISTS places")
# Rebuild table schema with full location fields
cursor.execute("""
    CREATE TABLE places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        city_village TEXT,
        street_name TEXT,
        landmark TEXT,
        location TEXT,
        address TEXT,
        description TEXT,
        map_embed TEXT,
        gallery TEXT
    )
""")

sample_places = [
    {
        "name": "Tirupati Sri Venkateswara Swamy Temple",
        "category": "Temples",
        "city_village": "Tirupati",
        "street_name": "S Mada Street",
        "landmark": "Near Seshachalam Seven Hills",
        "location": "Tirumala, Andhra Pradesh",
        "address": "S Mada St, Tirumala, Tirupati, Andhra Pradesh 517504",
        "description": "Ancient holy temple dedicated to Lord Venkateswara located atop the seven peaks of Seshachalam Hills.",
        "map_embed": "https://maps.google.com/maps?q=Tirupati+Venkateswara+Temple+Tirumala&t=&z=15&ie=UTF8&iwloc=&output=embed",
        "gallery": ["kashi.jpg"]
    },
    {
        "name": "Kashi Vishwanath Temple",
        "category": "Temples",
        "city_village": "Varanasi",
        "street_name": "Lahori Tola Road",
        "landmark": "Near Dashashwamedh Ghat & Ganges River",
        "location": "Varanasi, Uttar Pradesh",
        "address": "Lahori Tola, Varanasi, Uttar Pradesh 221001",
        "description": "One of the most famous Hindu temples dedicated to Lord Shiva, located on the western bank of the holy river Ganga.",
        "map_embed": "https://maps.google.com/maps?q=Kashi+Vishwanath+Temple+Varanasi&t=&z=15&ie=UTF8&iwloc=&output=embed",
        "gallery": ["kashi.jpg"]
    },
    {
        "name": "Sri Bhramaramba Mallikarjuna Temple",
        "category": "Temples",
        "city_village": "Srisailam",
        "street_name": "Temple Road",
        "landmark": "Near Krishna River & Nallamala Forest Range",
        "location": "Srisailam, Andhra Pradesh",
        "address": "Srisailam, Nandyal District, Andhra Pradesh 518101",
        "description": "A holy shrine that serves as both a Jyotirlinga and a Shakti Peetha on the Nallamala Hills.",
        "map_embed": "https://maps.google.com/maps?q=Srisailam+Mallikarjuna+Temple&t=&z=15&ie=UTF8&iwloc=&output=embed",
        "gallery": ["kashi.jpg"]
    },
    {
        "name": "Golden Temple (Harmandir Sahib)",
        "category": "Gurudwaras",
        "city_village": "Amritsar",
        "street_name": "Golden Temple Road",
        "landmark": "Near Amrit Sarovar Lake",
        "location": "Amritsar, Punjab",
        "address": "Golden Temple Rd, Atta Mandi, Katra Ahluwalia, Amritsar, Punjab 143006",
        "description": "The preeminent spiritual site of Sikhism, famous for its gold-plated central shrine surrounded by the sacred Amrit Sarovar tank.",
        "map_embed": "https://maps.google.com/maps?q=Golden+Temple+Amritsar&t=&z=15&ie=UTF8&iwloc=&output=embed",
        "gallery": ["golden.jpg"]
    },
    {
        "name": "Basilica of Bom Jesus",
        "category": "Churches",
        "city_village": "Old Goa",
        "street_name": "National Highway 4A",
        "landmark": "Near Archaeological Museum of Goa",
        "location": "Old Goa, Goa",
        "address": "Old Goa Road, Bainguinim, Goa 403402",
        "description": "A UNESCO World Heritage Site containing the mortal remains of Saint Francis Xavier.",
        "map_embed": "https://maps.google.com/maps?q=Basilica+of+Bom+Jesus+Goa&t=&z=15&ie=UTF8&iwloc=&output=embed",
        "gallery": ["church.jpg"]
    },
    {
        "name": "Jama Masjid",
        "category": "Mosques",
        "city_village": "New Delhi",
        "street_name": "Jama Masjid Road",
        "landmark": "Opposite Red Fort",
        "location": "Old Delhi, Delhi",
        "address": "Jama Masjid Rd, Chandni Chowk, New Delhi, Delhi 110006",
        "description": "One of the largest mosques in India, built by Mughal Emperor Shah Jahan between 1644 and 1656.",
        "map_embed": "https://maps.google.com/maps?q=Jama+Masjid+Delhi&t=&z=15&ie=UTF8&iwloc=&output=embed",
        "gallery": ["masjid.jpg"]
    }
]

for p in sample_places:
    cursor.execute("""
        INSERT INTO places (name, category, city_village, street_name, landmark, location, address, description, map_embed, gallery)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p["name"], p["category"], p["city_village"], p["street_name"],
        p["landmark"], p["location"], p["address"], p["description"],
        p["map_embed"], json.dumps(p["gallery"])
    ))

conn.commit()
conn.close()
print("Database reset and seeded successfully!")