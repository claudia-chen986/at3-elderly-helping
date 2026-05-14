from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder = "frontend/templetes"
)

@app.route('/')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)