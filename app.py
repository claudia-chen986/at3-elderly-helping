from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

#authentication imports
from authentication import (
    validate_email,
    validate_password,
    hash_password,
    verify_password
)

from journal_validation import validate_journal_entry

app = Flask(
    __name__,
    template_folder='templates'
)

app.permanent_session_lifetime = timedelta(minutes=30)
app.secret_key = 'Elderly_helping_app_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=db.func.current_timestamp())

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

    journal_entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.time.desc()).all()

    return render_template(
        'homepage.html',
        user=user,
        journal_entries=journal_entries
    )

@app.route('/save_journal', methods=['POST'])
def save_journal():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    content = request.form['content']

    validation_error = validate_journal_entry(
        title,
        content
    )

    if validation_error:
        return validation_error

    entry = JournalEntry(
        user_id=session['user_id'],
        title=title,
        content=content
    )

    db.session.add(entry)
    db.session.commit()

    return redirect(url_for('journal'))

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
    
    journal_entries = JournalEntry.query.filter_by(user_id=session['user_id']).order_by(JournalEntry.time.desc()).all()

    return render_template(
        'journal.html',
        journal_entries=journal_entries
    )



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

    session.clear()
    session.permanent = True
    session['user_id'] = user.id

    return redirect(url_for('homepage'))
    
#login user route
@app.route('/login_user', methods=['POST'])
def login_user():

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user and verify_password(user.password, password):
        session.clear()
        session.permanent = True
        session['user_id'] = user.id
        return redirect(url_for('homepage'))

    return "Invalid email or password"


if __name__ == '__main__':
    app.run(debug=True)