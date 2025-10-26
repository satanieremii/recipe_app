import os
from types import SimpleNamespace
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session, request, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import text
from models import db, User, Recipe
from forms import RegistrationForm, LoginForm, RecipeForm, SearchForm

# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

# demo flag: enable vulnerable search only when env var set
DEMO_SQLI_ENABLED = os.getenv("ENABLE_DEMO_SQLI", "0") == "1"

# ---------- DB init ----------
db.init_app(app)

# ensure uploads folder exists
os.makedirs(os.path.join(BASE_DIR, app.config['UPLOAD_FOLDER']), exist_ok=True)

# create tables at startup
with app.app_context():
    db.create_all()

# ---------- helpers ----------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)

# ---------- routes ----------
@app.route('/')
def index():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return render_template('index.html', recipes=recipes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists", "warning")
            return render_template('register.html', form=form)
        hashed = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash("Logged in", "success")
            return redirect(url_for('index'))
        flash("Invalid credentials", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out", "info")
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        user = current_user()
        if not user:
            flash("You must be logged in to add a recipe", "warning")
            return redirect(url_for('login'))

        # handle file
        filename = None
        file = form.image.data
        if file and file.filename:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(os.path.join(BASE_DIR, save_path))
            else:
                flash("File type not allowed", "danger")
                return render_template('add_recipe.html', form=form)

        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            image=filename,
            user_id=user.id
        )
        db.session.add(recipe)
        db.session.commit()
        flash("Recipe added", "success")
        return redirect(url_for('index'))
    return render_template('add_recipe.html', form=form)

@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', recipe=recipe)

# safe search (parameterized)
@app.route('/search_safe', methods=['GET'])
def search_safe():
    q = request.args.get('q', '').strip()
    rows = []
    if q:
        pattern = f"%{q}%"
        rows = Recipe.query.filter(Recipe.title.like(pattern)).all()
    form = SearchForm()
    return render_template('search.html', rows=rows, form=form, demo_enabled=False, demo_route='search_safe')

# vulnerable demo (registered only if flag enabled)
if DEMO_SQLI_ENABLED:
    @app.route('/search_vuln', methods=['GET'])
    def search_vuln():
        q = request.args.get('q', '')
        rows = []
        if q:
            raw_sql = f"SELECT id, title, description FROM recipe WHERE title LIKE '%{q}%'"
            result = db.session.execute(text(raw_sql)).fetchall()
            rows = [SimpleNamespace(id=r[0], title=r[1], description=r[2], image=None, created_at=None, author=None) for r in result]
        form = SearchForm()
        return render_template('search.html', rows=rows, form=form, demo_enabled=True, demo_route='search_vuln')

# serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(BASE_DIR, app.config['UPLOAD_FOLDER']), filename)

# ---------- run ----------
if __name__ == "__main__":
    app.run(debug=True)
