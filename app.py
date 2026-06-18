from flask import Flask, render_template, request, jsonify
import sqlite3
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import resend

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'portfolio.db')

GMAIL_USER = os.environ.get('GMAIL_USER')
GMAIL_PASS = os.environ.get('GMAIL_PASS')

# ── DB ────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            email        TEXT NOT NULL,
            subject      TEXT NOT NULL,
            message      TEXT NOT NULL,
            submitted_at DATETIME DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    print("✅ SQLite DB ready.")

# ── EMAIL ─────────────────────────────────────────────
def send_email_notification(name, email, subject, message):

    resend.api_key = os.getenv("RESEND_API_KEY")

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": GMAIL_USER,
        "subject": f"New Portfolio Message: {subject}",
        "html": f"""
        <h2>New Portfolio Contact</h2>

        <p><b>Name:</b> {name}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Subject:</b> {subject}</p>

        <p>{message}</p>
        """
    })

    print("✅ Email sent via Resend")

  

# ── ROUTES ────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    try:
        data    = request.get_json()
        name    = data.get('name', '').strip()
        email   = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'error': 'All fields are required.'}), 400

        conn = get_db()
        conn.execute(
            "INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)",
            (name, email, subject, message)
        )
        conn.commit()
        conn.close()

        send_email_notification(name, email, subject, message)

        return jsonify({'success': True, 'message': "Message sent! I'll get back to you soon 🚀"})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/messages')
def view_messages():
    conn = get_db()
    messages = conn.execute(
        "SELECT * FROM contact_messages ORDER BY submitted_at DESC"
    ).fetchall()
    conn.close()
    return render_template('messages.html', messages=messages)


# ── INIT DB (runs for both gunicorn on Render AND local) ──
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)