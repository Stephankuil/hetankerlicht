# ankerlicht_app.py
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("ANKERLICHT_SECRET_KEY", "defaultsecret")

USERNAME = os.getenv("ANKERLICHT_USERNAME")
PASSWORD = os.getenv("ANKERLICHT_PASSWORD")

print(f"Gebruikersnaam uit .env: {USERNAME}")
print(f"Wachtwoord uit .env: {PASSWORD}")

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('ankerlicht.db')
    conn.row_factory = sqlite3.Row
    return conn

# Homepagina - publiek toegankelijk
@app.route('/')
def home():
    return render_template('home.html')

# Portfolio / Over Het Ankerlicht
@app.route('/over')
def over():
    return render_template('over.html')

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
        titel = request.form['titel']
        foto_url = None
        video_url = None

        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto_url = f"/static/uploads/{filename}"

        if 'youtube_url' in request.form and request.form['youtube_url'].strip() != '':
            video_url = request.form['youtube_url'].strip()

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

if __name__ == '__main__':
    app.run(debug=True)
