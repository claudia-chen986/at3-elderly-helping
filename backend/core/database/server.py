# Import the necessary modules
from flask import Flask, render_template, request, redirect, url_for
from data import db, Task
from task import user_create_task, user_update_task, user_delete_task

# Create the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example_test_db.db'
db.init_app(app)

# WRITE YOUR CODE HERE
# route to dashboard
@app.route('/')
def dashboard():
	return render_template('dashboard.html')

# stub route for creating a task
@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')

        user_create_task(title, description, priority)

        return redirect(url_for('dashboard'))

    return render_template("create_task.html")

#stub route for deleting a task
@app.route('/delete_task', methods=['GET', 'POST'])
def delete_task():
    if request.method == 'POST':
        task_id = request.form.get('id')

        return redirect(url_for('dashboard'))

    return render_template("delete_task.html")

#stub route for updating a task
@app.route('/update_task', methods=['GET', 'POST'])
def update_task():
    if request.method == 'POST':
        task_id = request.form.get('id')

        return redirect(url_for('dashboard'))

    return render_template("update_task.html")

# Run the app
if __name__ == '__main__':
	app.run()