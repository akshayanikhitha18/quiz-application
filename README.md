# 🔮 QuizSphere

A pastel-purple quiz app for college students. Built with HTML, CSS, JavaScript, Python (Flask) and MySQL.

**Subjects:** OOP, DBMS, COA, Statistics, DSA, POM
**Features:** register/login, MCQ + True/False, 30s-per-question timer, auto scoring, explanations, history, performance dashboard, admin panel (add/delete questions).

## Folder layout
```
quizsphere/
  app.py          Flask backend + JSON API
  config.py       MySQL settings (edit your password here)
  schema.sql      Tables, keys, relationships and sample questions
  setup_db.py     Creates the database and the admin account
  requirements.txt
  static/         index.html, style.css, app.js (the frontend)
```

## Windows setup (step by step)

**1. Install the tools** (skip what you have)
- Python 3.10+ from https://www.python.org/downloads/ (tick **"Add Python to PATH"**)
- MySQL Community Server from https://dev.mysql.com/downloads/installer/ (remember your **root password**)

**2. Open Command Prompt in the project folder** (unzip first)
```
cd C:\path\to\quizsphere
```

**3. Create a virtual environment and install packages**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**4. Set your MySQL password** (use your real password, no quotes)
```
set DB_PASSWORD=your_root_password
```
Or open `config.py` and replace `your_mysql_password`.

**5. Create the database** (this also adds sample questions and the admin account)
```
python setup_db.py
```

**6. Start the app**
```
python app.py
```
Open **http://localhost:5000** in your browser.

## Logins
- Admin: `admin@quizsphere.com` / `admin123`
- Students: click **Create an account**

## Troubleshooting
- **"Database error"** → MySQL is not running (open *Services*, start *MySQL80*) or the password is wrong.
- **`python` not recognised** → reinstall Python with *Add to PATH* ticked.
- **Next time you open a new Command Prompt**, run `venv\Scripts\activate` and `set DB_PASSWORD=...` again, then `python app.py`.
- Running `setup_db.py` again **resets the database**.

## Database design
`users` 1—N `attempts` N—1 `subjects` 1—N `questions`; `attempts` 1—N `attempt_answers` N—1 `questions`. All links are foreign keys with `ON DELETE CASCADE`.
