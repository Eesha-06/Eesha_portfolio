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
        msg['From']    = GMAIL_USER
        msg['To']      = GMAIL_USER

        html = f"""
        <html><body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:20px;">
          <div style="max-width:560px;margin:auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
            <div style="background:linear-gradient(135deg,#6366F1,#A78BFA);padding:24px 30px;">
              <h2 style="color:#fff;margin:0;">New Message on Your Portfolio</h2>
            </div>
            <div style="padding:30px;">
              <table style="width:100%;border-collapse:collapse;">
                <tr><td style="padding:8px 0;color:#6b7280;font-size:13px;width:80px;">Name</td>
                    <td style="padding:8px 0;color:#111;font-weight:600;">{name}</td></tr>
                <tr><td style="padding:8px 0;color:#6b7280;font-size:13px;">Email</td>
                    <td style="padding:8px 0;"><a href="mailto:{email}" style="color:#6366F1;">{email}</a></td></tr>
                <tr><td style="padding:8px 0;color:#6b7280;font-size:13px;">Subject</td>
                    <td style="padding:8px 0;color:#111;">{subject}</td></tr>
              </table>
              <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;"/>
              <p style="color:#6b7280;font-size:13px;margin-bottom:8px;">Message</p>
              <p style="color:#111;line-height:1.7;background:#f9f9f9;padding:16px;border-radius:8px;border-left:4px solid #6366F1;">{message}</p>
              <div style="margin-top:24px;">
                <a href="mailto:{email}" style="background:#6366F1;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-size:14px;font-weight:600;">
                  Reply to {name}
                </a>
              </div>
            </div>
            <div style="background:#f9f9f9;padding:16px 30px;text-align:center;">
              <p style="color:#9ca3af;font-size:12px;margin:0;">Eesha Portfolio — Contact Form Notification</p>
            </div>
          </div>
        </body></html>
        """

        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())

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