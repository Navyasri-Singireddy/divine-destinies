import sqlite3

conn = sqlite3.connect("spiritual_places.db")
cursor = conn.cursor()

# Add granular location columns
for column in ["city_village", "street_name", "landmark"]:
    try:
        cursor.execute(f"ALTER TABLE places ADD COLUMN {column} TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

conn.commit()
conn.close()
print("Database schema updated with City/Village, Street Name, and Landmark columns!")