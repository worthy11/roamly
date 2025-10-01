import sqlite3
from pathlib import Path
from app.services.embedding_service import embedding_service

DB_PATH = Path(__file__).resolve().parent / "db" / "roamly.db"
DB_PATH.parent.mkdir(exist_ok=True)

schema = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    pass TEXT
);

CREATE TABLE IF NOT EXISTS trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_Id INTEGER NOT NULL,
    country TEXT NOT NULL,
    description TEXT,
    duration INTEGER,
    num_people INTEGER,
    activity_level TEXT,
    budget REAL,
    embedding BLOB,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    lat REAL,
    lon REAL
);

CREATE TABLE IF NOT EXISTS trip_cities (
    relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    city_id INTEGER NOT NULL,
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
);
"""

dummy_users = """
INSERT INTO users (name, email, pass) VALUES
('Alice Rossi', 'alice.rossi@example.com', 'password123'),
('Kenji Tanaka', 'kenji.tanaka@example.com', 'securepass1'),
('John Smith', 'john.smith@example.com', 'mypassword'),
('Claire Dubois', 'claire.dubois@example.com', 'passw0rd!'),
('Lucas Oliveira', 'lucas.oliveira@example.com', 'qwerty123'),
('Sophie Wilson', 'sophie.wilson@example.com', 'letmein'),
('Omar Hassan', 'omar.hassan@example.com', 'secretpass'),
('Maria Gonzalez', 'maria.gonzalez@example.com', '12345678'),
('Daniel Thompson', 'daniel.thompson@example.com', 'adminpass'),
('Anong Suksawat', 'anong.suksawat@example.com', 'pass1234');
"""

dummy_trips = [
((1, 'Italy', 'Romantic getaway exploring ancient ruins and Italian cuisine.', 7, 2, 'medium', 1800, None), ["Rome", "Florence", "Venice"]),
((2, 'Japan', 'Spring trip to see cherry blossoms and visit temples.', 10, 1, 'low', 2500, None), ["Tokyo"]),
((3, 'USA', 'Family road trip across California, beaches and national parks.', 14, 4, 'high', 5000, None),["Los Angeles", "San Francisco"]),
((4, 'France', 'Wine-tasting and art museums in Paris and Bordeaux.', 5, 2, 'low', 2200, None),["Paris", "Bordeaux", "Lyon"]),
((5, 'Brazil', 'Carnival experience in Rio with samba dancing and beaches.', 8, 3, 'high', 3000, None),["Rio de Janeiro", "São Paulo"]),
((6, 'Australia', 'Backpacking along the east coast, surfing and diving.', 21, 2, 'high', 4500, None),["Sydney", "Cairns", "Brisbane"]),
((7, 'Egypt', 'Historical trip visiting pyramids and Nile river cruise.', 6, 2, 'medium', 2000, None),["Cairo", "Luxor"]),
((8, 'Spain', 'Cultural immersion in Barcelona, flamenco in Seville.', 9, 2, 'medium', 2700, None),["Barcelona", "Madrid"]),
((9, 'Canada', 'Skiing in Whistler and hiking in Banff National Park.', 12, 3, 'high', 4000, None),["Vancouver", "Whistler"]),
((10, 'Thailand', 'Island-hopping and street food tour in Bangkok.', 11, 2, 'medium', 1600, None),["Bangkok", "Phuket", "Chiang Mai"])]

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

    cur.execute(dummy_users)

    print("Generating embeddings for trips...")
    for (trip, cities) in dummy_trips:
        user_id, country, description, duration, num_people, activity_level, budget, _ = trip
        
        trip_data = {
            "country": country,
            "description": description,
            "activity_level": activity_level,
            "duration": duration,
            "budget": budget
        }
        
        trip_text = embedding_service.generate_trip_text(trip_data)
        embedding = embedding_service.generate_embedding(trip_text)
        embedding_json = embedding_service.serialize_embedding(embedding)
        
        cur.execute("""
            INSERT INTO trips (user_id, country, description, duration, num_people, activity_level, budget, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, country, description, duration, num_people, activity_level, budget, embedding_json))

        trip_id = cur.lastrowid
        for city in cities:
            cur.execute("SELECT city_id FROM cities WHERE name=?", (city,))
            city_id = cur.fetchone()[0]
            
            cur.execute("INSERT INTO trip_cities (trip_id, city_id) VALUES (?, ?)", (trip_id, city_id))
        
        print(f"  ✓ Trip {trip_id}: {country} - {description[:50]}...")

    conn.commit()
    conn.close()
    print(f"Successfully inserted {len(dummy_trips)} trips with embeddings!")


if __name__ == "__main__":
    init_db()
    import_cities("worldcities.csv")
    insert_dummies()
