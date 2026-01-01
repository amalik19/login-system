from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from api import get_popular_movies

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20),unique = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")
        
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/dashboard', methods = ["GET", "POST"])
@login_required
def dashboard():
    movies = get_popular_movies()
    for movie in movies:
        if movie.get("poster_path"):
            movie["poster_path"] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
        else:
            movie["poster_path"] = "/static/no_image_available.png"
    return render_template('dashboard.html', movies=movies)

@app.route('/logout', methods = ["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods = ["GET", "POST"])
def register():
    form = RegisterForm()
    print("Form validation result:", form.validate_on_submit())
    
    if form.validate_on_submit():
        print("FORM VALIDATED")
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password = hashed_password)
        print("User object created:", new_user.username)
        db.session.add(new_user)
        print("User added to session")
        
        try:
            db.session.commit()
            print("COMMIT SUCCESS")
        except Exception as e:
            db.session.rollback()
            print("COMMIT FAILED:", e)
            
        print("User saved!")
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("DATABASE LOCATIONS: ", db.engine.url)
    app.run(debug=True)