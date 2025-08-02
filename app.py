# ankerlicht_app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import date
import re

load_dotenv()

from flask import Flask
import os

app = Flask(__name__, template_folder='templates')

# 🔐 Geheimen uit .env
app.secret_key = os.getenv("ANKERLICHT_SECRET_KEY", "defaultsecret")

USERNAME = os.getenv("ANKERLICHT_USERNAME")
PASSWORD = os.getenv("ANKERLICHT_PASSWORD")

print(f"Gebruikersnaam uit .env: {USERNAME}")
print(f"Wachtwoord uit .env: {PASSWORD}")

# 📂 Uploadfolders
UPLOAD_FOLDER_IMAGES = os.path.join(os.getcwd(), 'static', 'uploads')
UPLOAD_FOLDER_PDFS = os.path.join(os.getcwd(), 'static', 'pdfs')



UPLOAD_FOLDER_NIEUWTJES = os.path.join(os.getcwd(), 'static', 'uploads', 'nieuwtjes')
os.makedirs(UPLOAD_FOLDER_NIEUWTJES, exist_ok=True)




# 📁 Zorg dat mappen bestaan
os.makedirs(UPLOAD_FOLDER_IMAGES, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_PDFS, exist_ok=True)

# 📦 Configuratie
app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES
app.config['UPLOAD_FOLDER_PDFS'] = UPLOAD_FOLDER_PDFS
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # max 16MB

# ✅ Toegestane extensies
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


import re

def extract_youtube_id(url):
    """
    Haalt de YouTube video ID uit een URL.
    Ondersteunt youtu.be en youtube.com links.
    """
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_db_connection():
    conn = sqlite3.connect('ankerlicht.db')
    conn.row_factory = sqlite3.Row
    return conn

# Homepagina - publiek toegankelijk
@app.route('/')
def home():
    print("Flask app is gestart met home route actief")

    return render_template('home.html')

# Portfolio / Over Het Ankerlicht
@app.route('/over')
def over():
    vandaag = date.today().isoformat()  # 'YYYY-MM-DD' formaat
    conn = sqlite3.connect('ankerlicht.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Selecteer activiteiten van vandaag of later, gesorteerd op datum, max 3
    cursor.execute("""
        SELECT * FROM activiteiten 
        WHERE datum >= ? 
        ORDER BY datum ASC 
        LIMIT 3
    """, (vandaag,))
    activiteiten = cursor.fetchall()
    conn.close()
    return render_template('over.html', activiteiten=activiteiten)


@app.route('/over-ons')
def over_ons():
    return render_template('over_ons.html')

# Publieke agenda
@app.route('/agenda')
def publieke_agenda():
    conn = get_db_connection()
    activiteiten = conn.execute('SELECT * FROM activiteiten ORDER BY datum').fetchall()
    conn.close()
    return render_template('agenda.html', activiteiten=activiteiten)

# Contactpagina
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Fotopagina (publiek zichtbaar)
@app.route('/fotos')
def fotos():
    conn = get_db_connection()
    fotos = conn.execute('SELECT * FROM fotos ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('fotos.html', fotos=fotos)

# Foto of YouTube-video toevoegen (alleen voor beheerder)
@app.route('/fotos/nieuw', methods=['GET', 'POST'])
def foto_toevoegen():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        titel = request.form['titel'].strip()
        foto_url = None
        video_url = None

        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], filename))
                foto_url = f"/static/uploads/{filename}"

        if 'youtube_url' in request.form and request.form['youtube_url'].strip() != '':
            video_url = request.form['youtube_url'].strip()
            video_id = extract_youtube_id(video_url)
            if video_id and not foto_url:
                foto_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        if not titel:
            return "Titel is verplicht."

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO fotos (titel, foto_url, video_url) VALUES (?, ?, ?)',
            (titel, foto_url, video_url)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('fotos'))

    return render_template('foto_toevoegen.html')


@app.route('/fotos/verwijder/<int:foto_id>', methods=['POST'])
def foto_verwijderen(foto_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    foto = conn.execute('SELECT * FROM fotos WHERE id = ?', (foto_id,)).fetchone()

    if foto:
        # Verwijder het bestand uit de uploads-map
        if foto['foto_url']:
            bestand_pad = foto['foto_url'].replace("/static/", "static/")
            if os.path.exists(bestand_pad):
                os.remove(bestand_pad)

        conn.execute('DELETE FROM fotos WHERE id = ?', (foto_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('fotos'))


# Dashboard - alleen voor ingelogde beheerders
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    activiteiten = conn.execute('SELECT * FROM activiteiten ORDER BY datum').fetchall()
    conn.close()
    return render_template('index.html', activiteiten=activiteiten)

# Inloggen
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Ongeldige inloggegevens')
    return render_template('login.html')

# Uitloggen
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Agenda detailpagina
@app.route('/activiteit/<int:id>')
def activiteit_detail(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    activiteit = conn.execute('SELECT * FROM activiteiten WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('activiteit_detail.html', activiteit=activiteit)

# Activiteit verwijderen
@app.route('/activiteit/<int:id>/verwijderen', methods=['POST'])
def activiteit_verwijderen(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM activiteiten WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('activiteiten'))

# Activiteit bewerken
@app.route('/activiteit/<int:id>/bewerken', methods=['GET', 'POST'])
def activiteit_bewerken(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        titel = request.form['titel']
        datum = request.form['datum']
        beschrijving = request.form['beschrijving']
        conn.execute('UPDATE activiteiten SET titel = ?, datum = ?, beschrijving = ? WHERE id = ?',
                     (titel, datum, beschrijving, id))
        conn.commit()
        conn.close()
        return redirect(url_for('activiteit_detail', id=id))
    activiteit = conn.execute('SELECT * FROM activiteiten WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('activiteit_bewerken.html', activiteit=activiteit)

# Lid worden pagina
@app.route('/lidworden')
def lidworden():
    return render_template('lidworden.html')

from flask import Flask, render_template, request, redirect, url_for, flash
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()  # Voor .env-gegevens zoals e-mailwachtwoord



@app.route("/lidwordenemail", methods=["GET", "POST"])
def lid_worden():
    if request.method == "POST":
        naam = request.form["naam"]
        email = request.form["email"]
        bericht = request.form["bericht"]

        # 📨 E-mail versturen
        verzender = os.getenv("EMAIL_USER")
        wachtwoord = os.getenv("EMAIL_PASS")
        ontvanger = "jouw@emailadres.nl"

        body = f"Nieuw lidmaatschap via de website:\n\nNaam: {naam}\nE-mail: {email}\nBericht:\n{bericht}"
        msg = MIMEText(body)
        msg["Subject"] = "Nieuwe aanmelding Het Ankerlicht"
        msg["From"] = verzender
        msg["To"] = ontvanger

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(verzender, wachtwoord)
            server.send_message(msg)
            server.quit()
            flash("✅ Je bericht is verstuurd! We nemen snel contact met je op.", "success")
        except Exception as e:
            print(e)
            flash("❌ Er ging iets mis bij het verzenden van je bericht.", "error")

        return redirect(url_for("lid_worden"))

    return render_template("lidworden.html")

# Activiteitenoverzicht
@app.route('/activiteiten')
def activiteiten():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    activiteiten = conn.execute('SELECT * FROM activiteiten ORDER BY datum').fetchall()
    conn.close()
    return render_template('activiteit.html', activiteiten=activiteiten)

# Nieuwe activiteit aanmaken
@app.route('/activiteiten/nieuw', methods=['GET', 'POST'])
def activiteit_aanmaken():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        titel = request.form['titel']
        datum = request.form['datum']
        beschrijving = request.form['beschrijving']
        conn = get_db_connection()
        conn.execute('INSERT INTO activiteiten (titel, datum, beschrijving) VALUES (?, ?, ?)',
                     (titel, datum, beschrijving))
        conn.commit()
        conn.close()
        return redirect(url_for('activiteiten'))
    return render_template('activiteit_aanmaken.html')



@app.route('/verhuur')
def verhuur():
    return render_template('verhuur.html')

@app.route('/sponsers')
def sponsers():
    return render_template('sponsers.html')

@app.route('/krantje')
def krantje():
    return render_template('pdf_downloads.html')



@app.route("/upload_pdf", methods=["GET", "POST"])
def upload_pdf():
    if not session.get("logged_in"):
        flash("Log eerst in om PDF's te uploaden.")
        return redirect(url_for("login"))  # Zorg dat je een login-route hebt

    if request.method == "POST":
        if "pdf_file" not in request.files:
            flash("Geen bestand geselecteerd.")
            return redirect(request.url)
        file = request.files["pdf_file"]
        if file.filename == "":
            flash("Bestandsnaam is leeg.")
            return redirect(request.url)
        if file and file.filename.lower().endswith(".pdf"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER_PDFS"], file.filename)
            file.save(filepath)
            flash("Upload geslaagd!")
            return redirect(url_for("pdf_downloads"))
        else:
            flash("Alleen PDF-bestanden zijn toegestaan.")
            return redirect(request.url)

    return render_template("upload_pdf.html")

@app.route("/pdf_downloads")
def pdf_downloads():
    folder = app.config["UPLOAD_FOLDER_PDFS"]
    pdf_files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ]
    return render_template("pdf_downloads.html", pdfs=pdf_files)




@app.route('/nieuwtjes')
def nieuwtjes():
    print("✅ Route /nieuwtjes wordt aangeroepen!")
    conn = sqlite3.connect("ankerlicht.db")
    conn.row_factory = sqlite3.Row  # zodat je dict-achtige objecten krijgt
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nieuwtjes ORDER BY id DESC")
    artikelen = cursor.fetchall()
    conn.close()

    return render_template('nieuwtjes.html', artikelen=artikelen)

@app.route('/nieuwtjes/<int:nieuwtje_id>')
def nieuwtje_detail(nieuwtje_id):
    conn = sqlite3.connect("ankerlicht.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nieuwtjes WHERE id = ?", (nieuwtje_id,))
    artikel = cursor.fetchone()
    conn.close()

    if artikel:
        return render_template('nieuwtje_detail.html', artikel=artikel)
    return "Artikel niet gevonden", 404

import sqlite3

@app.route('/nieuwtjes/nieuw', methods=['GET', 'POST'])
def nieuwtjes_toevoegen():
    if request.method == 'POST':
        titel = request.form['titel']
        inhoud = request.form['inhoud']
        afbeelding = request.files['afbeelding']

        bestandsnaam = secure_filename(afbeelding.filename)
        pad = os.path.join(UPLOAD_FOLDER_NIEUWTJES, bestandsnaam)
        afbeelding.save(pad)

        # Sla op in de database
        conn = sqlite3.connect("ankerlicht.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nieuwtjes (titel, inhoud, afbeelding)
            VALUES (?, ?, ?)
        """, (titel, inhoud, f'uploads/nieuwtjes/{bestandsnaam}'))
        conn.commit()
        conn.close()

        return redirect(url_for('nieuwtjes'))

    return render_template('nieuwtjes_toevoegen.html')



if __name__ == '__main__':
    app.run(port=8000,debug=True)
