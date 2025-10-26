# Recipe App (Flask)

A small Flask web application to store and share recipes.

**Key features**
- User registration and login (passwords hashed with Werkzeug).
- Add recipes with optional image upload (stored in `static/uploads/`).
- View recipe with author and date (date shown as `DD.MM.YYYY`).
- Safe search endpoint `/search_safe` using parameterized queries (ORM).
- Local educational demo of a vulnerable search endpoint `/search_vuln` (SQL injection) — **disabled by default** and only enabled when the environment variable `ENABLE_DEMO_SQLI=1` is set.

> **Security note:** The vulnerable endpoint is included for educational/portfolio demonstration only. Do **not** enable `ENABLE_DEMO_SQLI` on any public or production server.

> **Licence & contact:** This project is for learning/portfolio purposes.
If you want to try improvements or have questions — open an issue/contact me.

---

## Screenshots

Include screenshots in `docs/` (examples):

- `docs/home.png` — Home page listing recipes  
- `docs/add_recipe.png` — Add recipe form with image upload  
- `docs/recipe.png` — Recipe page showing author, date and image  
- `docs/safe_search.png` — Safe search results  
- `docs/sql_injection_search_2.png` — Demo showing SQLi on `/search_vuln` locally

---

## Quick start (run locally)

1. Clone repo:

```bash
git clone https://github.com/satanieremii/recipe_app.git
cd recipe_app
```

2. Create virtual environment and install:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Prepare environment variables (example):

```bash
# generate a secure key and paste it
export SECRET_KEY='paste_a_generated_secret_here'
# enable demo vulnerable route only locally when you want to test
export ENABLE_DEMO_SQLI=0
```

You can create a local .env (NOT committed) and then source .env if preferred.

4. Run the app:

```bash
python app.py
# open http://127.0.0.1:5000
```

5. To enable the local SQLi demo (ONLY on your machine):

```bash
export ENABLE_DEMO_SQLI=1
python app.py
# then open /search_vuln and test payload like: %' OR '1'='1
```

Project structure
```
recipe_app/
├─ app.py
├─ models.py
├─ forms.py
├─ templates/
├─ static/
│  ├─ css/
│  └─ uploads/
├─ docs/
├─ requirements.txt
├─ .gitignore
├─ .env.example
└─ README.md
