import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

app = Flask(__name__)

# ─── MySQL Configuration ───────────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # Change to your MySQL Workbench username
    'password': 'root',  # Change to your MySQL Workbench password
    'database': 'eesha_portfolio'
}

def get_db_connection():
    """Create and return a MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        # First connect without database to create it
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()

        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # Create contact_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL,
                subject VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully.")
    except Error as e:
        print(f"❌ Error initializing database: {e}")

def send_notification_email(name, email, subject, message):

    sender_email = "eesha7430@gmail.com"
    app_password = "izcvgrnzfhmhrogs"

    body = f"""
New Portfolio Contact Form Submission

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""

    msg = MIMEText(body)

    msg['Subject'] = f"🚀 New Portfolio Message from {name}"
    msg['From'] = sender_email
    msg['To'] = sender_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        server.login(sender_email, app_password)

        server.send_message(msg)

        print("EMAIL SENT SUCCESSFULLY")

        server.quit()

    except Exception as e:
        print("EMAIL ERROR:", e)
    
# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    """Handle contact form submission and save to MySQL."""
    try:
        data = request.get_json()

        name    = data.get('name', '').strip()
        email   = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        # Basic validation
        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'error': 'All fields are required.'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed.'}), 500

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contact_messages (name, email, subject, message) VALUES (%s, %s, %s, %s)",
            (name, email, subject, message)
        )
        conn.commit()
        try:
            send_notification_email(name, email, subject, message)
        except Exception as e:
            print("EMAIL ERROR:", e)
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Message sent successfully! I\'ll get back to you soon 🚀'})

    except Error as e:
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/messages')
def view_messages():
    """Admin route to view all contact messages."""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contact_messages ORDER BY submitted_at DESC")
    messages = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('messages.html', messages=messages)


# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
