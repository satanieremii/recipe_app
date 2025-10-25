from flask import Flask, render_template, redirect, url_for, flash, session, request
from models import db, User, Recipe
from forms import RegistrationForm, LoginForm, RecipeForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_in_prod'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return render_template('index.html', recipes=recipes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Logged in')
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out')
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        if 'user_id' not in session:
            flash('Login required')
            return redirect(url_for('login'))
        recipe = Recipe(title=form.title.data, description=form.description.data, user_id=session['user_id'])
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe added')
        return redirect(url_for('index'))
    return render_template('add_recipe.html', form=form)

@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', recipe=recipe)

@app.route('/search_safe')
def search_safe():
    q = request.args.get('q', '')
    rows = []
    if q:
        sql = text("SELECT id, title FROM recipe WHERE title LIKE :pattern")
        pattern = f"%{q}%"
        result = db.session.execute(sql, {"pattern": pattern}).fetchall()
        rows = [{'id': r[0], 'title': r[1]} for r in result]
    return render_template('search.html', rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
