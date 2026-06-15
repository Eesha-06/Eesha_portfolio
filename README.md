# Eesha — Portfolio Website
**Flask + MySQL Workbench**

## 📁 Project Structure
```
eesha-portfolio/
├── app.py                  ← Flask backend (routes + DB)
├── requirements.txt        ← Python dependencies
├── templates/
│   ├── index.html          ← Main portfolio page
│   └── messages.html       ← Admin: view contact form submissions
└── static/
    ├── css/style.css       ← All styles
    ├── js/main.js          ← Navbar, typed effect, AJAX form
    └── assets/
        └── resume.pdf      ← Add your resume here
```

---

## ⚙️ Setup Instructions

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up MySQL via MySQL Workbench
1. Open **MySQL Workbench**
2. Connect to your local MySQL server
3. The database `eesha_portfolio` and the `contact_messages` table are **created automatically** when you run the app.
4. Open `app.py` and update your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',           # ← your MySQL username
    'password': 'your_password',  # ← your MySQL password
    'database': 'eesha_portfolio'
}
```

### 3. Add your Resume
Place your resume PDF at:
```
static/assets/resume.pdf
```

### 4. Update your personal links
In `templates/index.html`, replace placeholder links:
- GitHub URL
- LinkedIn URL
- Email address
- Instagram URL

### 5. Run the app
```bash
python app.py
```
Open your browser at: **http://localhost:5000**

---

## 📬 Viewing Contact Form Submissions
Visit: **http://localhost:5000/messages**

This shows all messages saved to MySQL in a clean admin table.

---

## 🗄️ MySQL Table Created Automatically
```sql
CREATE TABLE contact_messages (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100)  NOT NULL,
    email        VARCHAR(150)  NOT NULL,
    subject      VARCHAR(200)  NOT NULL,
    message      TEXT          NOT NULL,
    submitted_at DATETIME      DEFAULT CURRENT_TIMESTAMP
);
```
