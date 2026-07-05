from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
import calendar

#authentication imports
from authentication import (
    validate_email,
    validate_password,
    hash_password,
    verify_password,
    generate_token,
    generate_csrf_token,
    validate_csrf_token
)

from journal_validation import validate_journal_entry

app = Flask(
    __name__,
    template_folder='templates'
)

app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.secret_key = 'Elderly_helping_app_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    session_token = db.Column(db.String(255), nullable=True)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=db.func.current_timestamp())

class DailyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_name = db.Column(db.String(255), nullable=False)
    task_date =  db.Column(db.Date,nullable=False)
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def login():
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf_token()
    return render_template('login.html',csrf_token=session.get('csrf_token'))

@app.route('/signup')
def signup():
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf_token()
    return render_template('signup.html', csrf_token=session.get('csrf_token'))

@app.route('/forgot_password')
def forgot_password():
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf_token()
    return render_template('forgot-password.html', csrf_token=session.get('csrf_token'))

def validate_session():

    if (
        'user_id' not in session or
        'session_token' not in session
    ):
        return None

    user = User.query.get(session['user_id'])

    if not user:
        return None

    if user.session_token != session['session_token']:
        session.clear()
        return None

    return user

@app.route('/homepage')
def homepage():

    user = validate_session()

    if not user:
        return redirect(url_for('login'))

    journal_entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.time.desc()).all()

    return render_template(
        'homepage.html',
        user=user,
        journal_entries=journal_entries,
        csrf_token=session.get('csrf_token')
    )

@app.route('/logout')
def logout():

    if 'user_id' in session:
        user = User.query.get(session['user_id'])

        if user:
            user.session_token = None
            db.session.commit()

    session.clear()

    return redirect(url_for('login'))

@app.route('/daily_task')
def daily_task():

    user = validate_session()

    if not user:
        return redirect(url_for('login'))
    
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    day = request.args.get('day', datetime.now().day, type=int)

    calendar_days = calendar.monthcalendar(year, month)

    tasks_query = DailyTask.query.filter_by(user_id=user.id)

    if day:
        tasks_query = tasks_query.filter(
            db.extract('day', DailyTask.task_date) == day,
            db.extract('month', DailyTask.task_date) == month,
            db.extract('year', DailyTask.task_date) == year
        )

    tasks = tasks_query.order_by(
        DailyTask.task_date
    ).all()

    month_tasks = DailyTask.query.filter_by(user_id=user.id).filter(
    db.extract('month', DailyTask.task_date) == month,
    db.extract('year', DailyTask.task_date) == year
    ).all()

    task_days = [
    task.task_date.day
    for task in month_tasks
    ]

    month_name = calendar.month_name[month]

    return render_template(
        'daily_task.html',
        tasks=tasks,
        calendar_days=calendar_days,
        task_days=task_days,
        month=month,
        year=year,
        month_name=month_name,
        selected_day=day,
        csrf_token=session.get('csrf_token')
    )

@app.route('/add_task', methods=['POST'])
def add_task():

    user = validate_session()

    if not user:
        return redirect(url_for('login'))
    
    if not validate_csrf_token(request.form.get('csrf_token')):
        return "Invalid CSRF token.", 403

    task_name = request.form['task_name']
    task_date = datetime.strptime(request.form['task_date'],'%Y-%m-%d').date()

    if not task_name.strip():
        return "Task name cannot be empty."

    task = DailyTask(
        user_id=user.id,
        task_name=task_name,
        task_date=task_date
    )

    db.session.add(task)
    db.session.commit()

    return redirect(url_for('daily_task'))

@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    
    user = validate_session()

    if not user:
        return redirect(url_for('login'))
    
    if not validate_csrf_token(request.form.get('csrf_token')):
        return "Invalid CSRF token.", 403

    task = DailyTask.query.get(task_id)

    if not task or task.user_id != user.id:
        return "Task not found."

    task.completed = True
    db.session.commit()

    return redirect(url_for('daily_task'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):

    user = validate_session()

    if not user:
        return redirect(url_for('login'))
    
    if not validate_csrf_token(request.form.get('csrf_token')):
        return "Invalid CSRF token.", 403

    task = DailyTask.query.get(task_id)

    if not task or task.user_id != user.id:
        return "Task not found."

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('daily_task'))
 
@app.route('/journal')
def journal():

    user = validate_session()

    if not user:
        return redirect(url_for('login'))

    journal_entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.time.desc()).all()

    return render_template(
        'journal.html',
        journal_entries=journal_entries,
        csrf_token=session.get('csrf_token')
    )

@app.route('/save_journal', methods=['POST'])
def save_journal():
    user = validate_session()

    if not user:
        return redirect(url_for('login'))
    
    if not validate_csrf_token(request.form.get('csrf_token')):
        return "Invalid CSRF token.", 403

    title = request.form['title']
    content = request.form['content']

    validation_error = validate_journal_entry(
        title,
        content
    )

    if validation_error:
        return validation_error

    entry = JournalEntry(
        user_id=user.id,
        title=title,
        content=content
    )

    db.session.add(entry)
    db.session.commit()

    return redirect(url_for('journal'))

@app.route('/delete_journal/<int:entry_id>', methods=['POST'])
def delete_journal(entry_id):

    user = validate_session()

    if not user:
        return redirect(url_for('login'))
    
    if not validate_csrf_token(request.form.get('csrf_token')):
        return "Invalid CSRF token.", 403

    entry = JournalEntry.query.get(entry_id)

    if not entry or entry.user_id != user.id:
        return "Journal entry not found."

    db.session.delete(entry)
    db.session.commit()

    return redirect(url_for('journal'))

#sign up user route
@app.route('/signup_user', methods=['POST'])
def signup_user():

    if not validate_csrf_token(request.form.get('csrf_token')):
        return "Invalid CSRF token.", 403
    
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

    token = generate_token()

    user.session_token = token
    db.session.commit()

    session.clear()
    session.permanent = True

    session['user_id'] = user.id
    session['session_token'] = token
    session['csrf_token'] = generate_csrf_token()

    return redirect(url_for('homepage'))
    
#login user route
@app.route('/login_user', methods=['POST'])
def login_user():

    if not validate_csrf_token(request.form.get('csrf_token')):
        return "Invalid CSRF token.", 403
    
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user and verify_password(user.password, password):
        token = generate_token()

        user.session_token = token
        db.session.commit()

        session.clear()
        session.permanent = True

        session['user_id'] = user.id
        session['session_token'] = token
        session['csrf_token'] = generate_csrf_token()

        return redirect(url_for('homepage'))
    
    return "Invalid email or password"


if __name__ == '__main__':
    app.run(debug=True, port=5173)