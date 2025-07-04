import sqlite3

conn = sqlite3.connect("ankerlicht.db")
cursor = conn.cursor()

# Maak de activiteiten-tabel aan
cursor.execute("""
CREATE TABLE IF NOT EXISTS activiteiten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    datum TEXT NOT NULL,
    beschrijving TEXT
)
""")

# Maak de leden-tabel aan
cursor.execute("""
CREATE TABLE IF NOT EXISTS leden (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    email TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE fotos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    foto_url TEXT,
    video_url TEXT
);
""")


conn.commit()
conn.close()
print("Database en tabellen aangemaakt.")
