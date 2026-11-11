
from flask import Flask, render_template, request
import sqlite3
import json

app = Flask(__name__)


# ----------------------------------
# DATABASE CONNECTION
# ----------------------------------

def get_db_connection():
    conn = sqlite3.connect('spiritual_places.db')
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------------
# CATEGORY INFORMATION
# ----------------------------------

CATEGORIES = [
    {"name": "Temples", "icon": "🛕"},
    {"name": "Churches", "icon": "⛪"},
    {"name": "Mosques", "icon": "🕌"},
    {"name": "Buddhist Places", "icon": "☸️"},
    {"name": "Gurudwaras", "icon": "🪯"},
    {"name": "Jain Places", "icon": "🙏"},
    {"name": "Sacred Nature", "icon": "🌿"},
]


# ----------------------------------
# CATEGORY IMAGES AND DESCRIPTIONS
# ----------------------------------

CATEGORY_META = {
    "Temples": {
        "image": "kashi.jpg",
        "desc": "Discover India's beautiful temples, ancient architecture and sacred traditions."
    },

    "Churches": {
        "image": "kashi.jpg",
        "desc": "Explore historic churches and important Christian heritage places in India."
    },

    "Mosques": {
        "image": "kashi.jpg",
        "desc": "Discover India's historic mosques and beautiful Islamic architecture."
    },

    "Buddhist Places": {
        "image": "kashi.jpg",
        "desc": "Explore peaceful Buddhist monasteries, stupas and pilgrimage destinations."
    },

    "Gurudwaras": {
        "image": "kashi.jpg",
        "desc": "Discover sacred Sikh places and their traditions of service and equality."
    },

    "Jain Places": {
        "image": "kashi.jpg",
        "desc": "Explore beautiful Jain temples and places of spiritual heritage."
    },

    "Sacred Nature": {
        "image": "kashi.jpg",
        "desc": "Experience India's peaceful sacred landscapes and natural wonders."
    }
}


# ----------------------------------
# GALLERY IMAGE HANDLING
# ----------------------------------

def process_places(rows):
    places = []

    for row in rows:
        place = dict(row)

        try:
            gallery_data = place.get('gallery')

            if gallery_data:
                place['gallery'] = json.loads(gallery_data)
            else:
                place['gallery'] = ["kashi.jpg"]

        except (json.JSONDecodeError, TypeError):
            place['gallery'] = ["kashi.jpg"]

        places.append(place)

    return places


# ----------------------------------
# HOME PAGE
# ----------------------------------

@app.route('/')
def home():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, COUNT(*) AS count
        FROM places
        GROUP BY category
    """)

    rows = cursor.fetchall()
    conn.close()

    categories = []

    for row in rows:

        cat_name = row['category']

        # Find matching category icon
        icon = next(
            (
                cat['icon']
                for cat in CATEGORIES
                if cat['name'] == cat_name
            ),
            "🌿"
        )

        # Get category image and description
        meta = CATEGORY_META.get(
            cat_name,
            {
                "image": "kashi.jpg",
                "desc": f"Explore {cat_name} in India."
            }
        )

        categories.append({
            "name": cat_name,
            "icon": icon,
            "count": row['count'],
            "image": meta["image"],
            "desc": meta["desc"]
        })

    return render_template(
        'index.html',
        categories=categories
    )


# ----------------------------------
# CATEGORY PLACES PAGE
# ----------------------------------

@app.route('/category/<category_name>')
def category_places(category_name):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM places
        WHERE category = ?
        ORDER BY name ASC
    """, (category_name,))

    rows = cursor.fetchall()
    conn.close()

    places = process_places(rows)

    return render_template(
        'category.html',
        category=category_name,
        places=places
    )


# ----------------------------------
# SEARCH PAGE
# ----------------------------------

@app.route('/search')
def search():

    query = request.args.get('query', '').strip()

    if not query:
        return render_template(
            'search_results.html',
            query="",
            places=[]
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    search_term = f"%{query.lower()}%"

    cursor.execute("""
        SELECT *
        FROM places
        WHERE LOWER(name) LIKE ?
           OR LOWER(city_village) LIKE ?
           OR LOWER(location) LIKE ?
           OR LOWER(category) LIKE ?
        ORDER BY name ASC
    """, (
        search_term,
        search_term,
        search_term,
        search_term
    ))

    rows = cursor.fetchall()
    conn.close()

    places = process_places(rows)

    return render_template(
        'search_results.html',
        query=query,
        places=places
    )


# ----------------------------------
# RUN FLASK APPLICATION
# ----------------------------------

if __name__ == '__main__':
    app.run(
        debug=True,
        port=5000
    )
