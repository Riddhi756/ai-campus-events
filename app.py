from flask import Flask, render_template, request, redirect, session,flash
import mysql.connector
from datetime import date
from datetime import datetime
import pytesseract
from PIL import Image
import pdfplumber
import os
from docx import Document
from werkzeug.utils import secure_filename
from ai.event_extractor import extract_event_info
from ai.event_summarizer import summarize_event
from ai.text_extractor import extract_text_from_image, extract_text_from_pdf,extract_text_from_docx
from ai.google_ocr import extract_text_google
from dotenv import load_dotenv

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPLOAD_FOLDER = "static/uploads/events"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


@app.route('/')
def home():
    return render_template('index.html')

# ---------- ADMIN LOGIN ----------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin' in session:
        return redirect('/admin/dashboard')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )
        admin = cursor.fetchone()

        if admin:
            session['admin'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

# ---------- ADMIN DASHBOARD ----------
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin/login')
    return render_template('admin_dashboard.html')

@app.route('/admin/add-event', methods=['GET', 'POST'])
def add_event():
    if 'admin' not in session:
        return redirect('/admin/login')

    cursor = db.cursor(dictionary=True)
    error = None

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        venue = request.form['venue']

        # 👇 FROM AI UPLOAD
        source_text = session.get('temp_text', '')
        attachments = session.get('uploaded_files', '')

        cursor.execute(
            "SELECT id FROM events WHERE title=%s AND event_date=%s",
            (title, event_date)
        )
        if cursor.fetchone():
            error = "Event with same title and date already exists"
        else:
            cursor.execute("""
                INSERT INTO events
                (title, description, event_date, event_time, venue, source_text, attachments)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                title,
                description,
                event_date,
                event_time,
                venue,
                source_text,
                attachments
            ))
            db.commit()

            # clear session after save
            session.pop('temp_text', None)
            session.pop('uploaded_files', None)

            return redirect('/admin/dashboard')

    return render_template('add_event.html', error=error)

@app.route('/admin/upload-source', methods=['GET', 'POST'])
def upload_source():
    if 'admin' not in session:
        return redirect('/admin/login')

    if 'temp_text' not in session:
        session['temp_text'] = ""

    if request.method == 'POST':
        uploaded_files = request.files.getlist('source_files')
        pasted_text = request.form.get('source_text')

        added = False

        saved_files = (
            session.get('uploaded_files', '').split(',')
            if session.get('uploaded_files')
            else []
        )

        # 🔹 Pasted text (WhatsApp / notice)
        if pasted_text:
            session['temp_text'] += pasted_text + "\n"
            added = True

        # 🔹 File upload + text extraction
        for file in uploaded_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                saved_files.append(filename)

                extracted_text = ""

                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    extracted_text = extract_text_from_image(filepath)

                elif filename.lower().endswith('.pdf'):
                    extracted_text = extract_text_from_pdf(filepath)

                elif filename.lower().endswith('.docx'):
                    extracted_text = extract_text_from_docx(filepath)

                if extracted_text:
                    session['temp_text'] += f"\n--- {filename} ---\n"
                    session['temp_text'] += extracted_text + "\n"
                    added = True

        session['uploaded_files'] = ",".join(saved_files)

        if added:
            flash("✅ Source uploaded & text extracted successfully.")

        return redirect('/admin/upload-source')

    return render_template('upload_source.html')


@app.route('/admin/process-event', methods=['POST'])
def process_event():
    if 'admin' not in session:
        return redirect('/admin/login')

    full_text = session.get('temp_text', '')

    if not full_text.strip():
        flash("❌ No source content found. Please add source first.")
        return redirect('/admin/upload-source')

    # AI processing
    short_description = summarize_event(full_text)
    extracted = extract_event_info(full_text)

    extracted['short_description'] = short_description

    # Store preview in session
    session['event_preview'] = extracted
    session['full_text'] = full_text

    return redirect('/admin/event-preview')


@app.route('/admin/event-preview')
def event_preview():
    if 'admin' not in session:
        return redirect('/admin/login')

    event = session.get('event_preview')
    full_text = session.get('full_text')

    # 🔍 Check missing fields
    missing_fields = []
    for field in ['title', 'event_date', 'event_time', 'venue']:
        if not event.get(field):
            missing_fields.append(field)

    return render_template(
        'event_preview.html',
        event=event,
        full_text=full_text,
        missing_fields=missing_fields
    )


@app.route('/admin/clear-sources')
def clear_sources():
    session.pop('temp_text', None)
    return redirect('/admin/upload-source')

@app.route('/admin/save-event', methods=['POST'])
def save_event():
    if 'admin' not in session:
        return redirect('/admin/login')

    title = request.form['title']
    description = request.form['description']
    event_date = request.form['event_date']
    event_time = request.form['event_time']
    venue = request.form['venue']

    cursor = db.cursor()

    # Duplicate check
    cursor.execute(
        "SELECT id FROM events WHERE title=%s AND event_date=%s",
        (title, event_date)
    )
    if cursor.fetchone():
        return "Duplicate event detected"

    cursor.execute(
        "INSERT INTO events (title, description, event_date, event_time, venue) VALUES (%s,%s,%s,%s,%s)",
        (title, description, event_date, event_time, venue)
    )
    db.commit()

    session.pop('ai_event', None)

    return redirect('/admin/dashboard')

@app.route('/student/dashboard')
def student_dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT *
        FROM events
        WHERE event_date >= CURDATE()
        ORDER BY event_date ASC, event_time ASC
    """)
    events = cursor.fetchall()
    # Convert string date to formatted string
    for event in events:
        if event['event_date']:
            event['formatted_date'] = datetime.strptime(str(event['event_date']), "%Y-%m-%d").strftime("%d %b %Y")
    return render_template('student_dashboard.html', events=events)

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
