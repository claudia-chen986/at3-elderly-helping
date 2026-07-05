import secrets
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
import re

def validate_email(email):

    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if not re.match(email_pattern, email):
        return "Invalid email format."

    return None

def validate_password(password):

    if len(password) < 8:
        return "Password must be at least 8 characters."

    if not any(char.isupper() for char in password):
        return "Password must include at least 1 capital letter."

    if not any(char.islower() for char in password):
        return "Password must include at least 1 lowercase letter."

    if not any(char in "!@#$%^&*()-_=+[]|;:',.<>?/" for char in password):
        return "Password must include at least 1 special character."

    if not any(char.isdigit() for char in password):
        return "Password must include at least 1 number."

    return None

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

def generate_token():
    return secrets.token_hex(32)

def generate_csrf_token():
    return secrets.token_hex(32)

def validate_csrf_token(form_token):
    if 'csrf_token' not in session:
        return False
    
    return session['csrf_token'] == form_token