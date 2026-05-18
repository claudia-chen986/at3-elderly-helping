from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

#hashing
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(
    __name__,
    template_folder='templates'
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
    return render_template('homepage.html')



#sign up user route
@app.route('/signup_user', methods=['POST'])
def signup_user():

    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return "Email already registered."
    
    if password != confirm_password:
        return "Password not matching, please check your password."

    hashed_password = generate_password_hash(password)
    
    user = User(
        email=email,
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('homepage'))
    
#login user route
@app.route('/login_user', methods=['POST'])
def login_user():

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return redirect(url_for('homepage'))
        
    return "Invalid email or password"


if __name__ == '__main__':
    app.run(debug=True)