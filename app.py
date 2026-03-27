from flask import Flask, render_template, request, redirect, url_for

from datetime import datetime

app = Flask(__name__)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/overview')
def overview():
    return render_template('overview.html')

if __name__ == '__main__':
    app.run(debug=True)
