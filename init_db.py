import sqlite3

conn = sqlite3.connect("ankerlicht.db")
cursor = conn.cursor()

# Maak de activiteiten-tabel aan
cursor.execute("""
CREATE TABLE IF NOT EXISTS activiteiten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    datum TEXT NOT NULL,
    tijd TEXT,
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

# Maak de foto's-tabel aan
cursor.execute("""
CREATE TABLE IF NOT EXISTS fotos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    foto_url TEXT,
    video_url TEXT
)
""")

# Maak de nieuwtjes-tabel aan
cursor.execute("""
CREATE TABLE IF NOT EXISTS nieuwtjes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    inhoud TEXT NOT NULL,
    afbeelding TEXT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("✅ Database en tabellen aangemaakt.")
