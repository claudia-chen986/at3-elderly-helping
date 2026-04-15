from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
# ADD YOUR CODE HERE
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.Integer, default=0)
    is_complete = db.Column(db.Boolean, default=False)