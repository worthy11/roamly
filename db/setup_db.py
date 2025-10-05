import sqlite3
from pathlib import Path
from app.services.embedding_service import embedding_service

DB_PATH = Path(__file__).resolve().parent / "roamly.db"
DB_PATH.parent.mkdir(exist_ok=True)

schema = """
CREATE TABLE IF NOT EXISTS trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    duration INTEGER,
    num_people INTEGER,
    activity_level TEXT,
    budget REAL,
    cities TEXT,
    lat REAL,
    lng REAL,
    embedding BLOB
);
"""

dummy_trips = [
    ('Romantic Italian Getaway', 'Romantic getaway exploring ancient ruins and Italian cuisine.', 7, 2, 'medium', 1800, 'Rome, Florence, Venice', 41.9028, 12.4964, None),
    ('Cherry Blossom Adventure', 'Spring trip to see cherry blossoms and visit temples.', 10, 1, 'low', 2500, 'Tokyo', 35.6762, 139.6503, None),
    ('California Road Trip', 'Family road trip across California, beaches and national parks.', 14, 4, 'high', 5000, 'Los Angeles, San Francisco', 34.0522, -118.2437, None),
    ('French Wine Tour', 'Wine-tasting and art museums in Paris and Bordeaux.', 5, 2, 'low', 2200, 'Paris, Bordeaux, Lyon', 48.8566, 2.3522, None),
    ('Carnival in Rio', 'Carnival experience in Rio with samba dancing and beaches.', 8, 3, 'high', 3000, 'Rio de Janeiro, São Paulo', -22.9068, -43.1729, None),
    ('Australian Adventure', 'Backpacking along the east coast, surfing and diving.', 21, 2, 'high', 4500, 'Sydney, Cairns, Brisbane', -33.8688, 151.2093, None),
    ('Egyptian History Tour', 'Historical trip visiting pyramids and Nile river cruise.', 6, 2, 'medium', 2000, 'Cairo, Luxor', 30.0444, 31.2357, None),
    ('Spanish Culture Trip', 'Cultural immersion in Barcelona, flamenco in Seville.', 9, 2, 'medium', 2700, 'Barcelona, Madrid', 41.3851, 2.1734, None),
    ('Canadian Wilderness', 'Skiing in Whistler and hiking in Banff National Park.', 12, 3, 'high', 4000, 'Vancouver, Whistler', 49.2827, -123.1207, None),
    ('Thai Island Hopping', 'Island-hopping and street food tour in Bangkok.', 11, 2, 'medium', 1600, 'Bangkok, Phuket, Chiang Mai', 13.7563, 100.5018, None)
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(schema)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

import pandas as pd

def import_cities(csv_path="worldcities.csv"):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_csv(csv_path)

    df = df.rename(columns={
        "city": "name",
        "country": "country",
        "lat": "lat",
        "lng": "lon"
    })

    df[["name", "country", "lat", "lon"]].to_sql(
        "cities", conn, if_exists="append", index=False
    )

    conn.close()
    print(f"Imported {len(df)} cities into database.")

def insert_dummies():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Generating embeddings for trips (description only)...")
    for trip_data in dummy_trips:
        title, description, duration, num_people, activity_level, budget, cities, lat, lng, _ = trip_data
        
        embedding = embedding_service.generate_embedding(description)
        embedding_json = embedding_service.serialize_embedding(embedding)
        
        cur.execute("""
            INSERT INTO trips (title, description, duration, num_people, activity_level, budget, cities, lat, lng, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, description, duration, num_people, activity_level, budget, cities, lat, lng, embedding_json))

        trip_id = cur.lastrowid
        print(f"  ✓ Trip {trip_id}: {title} - {description[:50]}...")

    conn.commit()
    conn.close()
    print(f"Successfully inserted {len(dummy_trips)} trips with embeddings!")


if __name__ == "__main__":
    init_db()
    insert_dummies()
