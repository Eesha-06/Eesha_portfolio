from flask import Flask, render_template, request, jsonify
import sqlite3
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📬 New Contact Form Message: {subject}"
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER

        html = f"""
        <html>
        <body>
            <h2>New Portfolio Message</h2>
            <p><b>Name:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Subject:</b> {subject}</p>
            <p><b>Message:</b> {message}</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        print("STEP 1: Starting SMTP")

        with smtplib.SMTP_SSL(
            'smtp.gmail.com',
            465,
            timeout=10
        ) as server:

            print("STEP 2: Logging in")
            server.login(GMAIL_USER, GMAIL_PASS)

            print("STEP 3: Sending")
            server.sendmail(
                GMAIL_USER,
                GMAIL_USER,
                msg.as_string()
            )

            print("STEP 4: Done")

        print(f"✅ Email notification sent for message from {name}")

    except Exception as e:
        print(f"⚠️ Email failed (message still saved to DB): {e}")

  

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