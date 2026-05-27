from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy

#authentication imports
from authentication import (
    validate_email,
    validate_password,
    hash_password,
    verify_password
)

app = Flask(
    __name__,
    template_folder='templates'
)

app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/homepage')
def homepage():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    return render_template(
        'homepage.html',
        user_name=user.name
    )

@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))

@app.route('/daily_task')
def daily_task():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('daily_task.html')


@app.route('/journal')
def journal():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('journal.html')


#sign up user route
@app.route('/signup_user', methods=['POST'])
def signup_user():

    name = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return "Email already registered."

    if password != confirm_password:
        return "Password not matching, please check your password."

    # Validate email
    email_error = validate_email(email)
    if email_error:
        return email_error

    # Validate password
    password_error = validate_password(password)
    if password_error:
        return password_error

    # Hash password
    hashed_password = hash_password(password)

    user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id

    return redirect(url_for('homepage'))
    
#login user route
@app.route('/login_user', methods=['POST'])
def login_user():

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user and verify_password(user.password, password):
        session['user_id'] = user.id
        return redirect(url_for('homepage'))

    return "Invalid email or password"


if __name__ == '__main__':
    app.run(debug=True)