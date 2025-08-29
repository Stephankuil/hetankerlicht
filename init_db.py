import sqlite3

conn = sqlite3.connect("ankerlicht.db")
cursor = conn.cursor()

# Tabellen aanmaken (één statement per execute)
cursor.execute("""
CREATE TABLE IF NOT EXISTS activiteiten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    datum TEXT NOT NULL,
    tijd TEXT,
    beschrijving TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS leden (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    email TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fotos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    foto_url TEXT,
    video_url TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nieuwtjes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    inhoud TEXT NOT NULL,
    afbeelding TEXT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bezoekers (
    id INTEGER PRIMARY KEY,
    aantal INTEGER NOT NULL
)
""")

# Startrecord voor teller: voorkom duplicate met OR IGNORE
cursor.execute("""
INSERT OR IGNORE INTO bezoekers (id, aantal) VALUES (1, 0)
""")

conn.commit()
conn.close()
print("✅ Database en tabellen aangemaakt.")
