from flask import Flask, render_template, url_for, redirect, request
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from tables import db, User, User_Preference
from api import get_popular_movies
from similarity import genre_map, genre_names, vectorise_movie, vectorise_user
import os

app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'database.db')}"
app.config['SECRET_KEY'] = 'thisisasecretkey'

db.init_app(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    if current_user.quiz_completed == False:
        return redirect(url_for('quiz'))
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

@app.route('/quiz', methods = ["GET", "POST"])     
@login_required
def quiz():
    if request.method == "POST":
        for i in genre_names:
            score = int(request.form[i])
            preference = User_Preference(user_id=current_user.id, genre=i, score=score)
            db.session.add(preference)
        current_user.quiz_completed = True
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('quiz.html', genres=genre_names)

if __name__ == '__main__':
    with app.app_context():
            db.create_all()
            print("DATABASE LOCATIONS: ", db.engine.url)
app.run(debug=True, port = 5001)    