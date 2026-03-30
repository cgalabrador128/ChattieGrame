from flask import Flask, flash, render_template, request, redirect, url_for
import data as dat
from datetime import datetime
import uuid
from data import loginUser

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = dat.loginUser(email, password)

        if user and email and password:
            flash('Login successful!')
            return redirect(url_for('overview'))

        else:
            error = "Invalid email or password. Please try again."
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            return render_template('signup.html', error="All fields are required")

        result = dat.signupUser(name, email, password)
        if result:
            flash('Signup successful! Please check your email to verify your account.')
            return redirect(url_for('overview'))
        else:
            return render_template('signup.html', error="Signup failed. Please try again.")

    return render_template('signup.html')


@app.route('/overview')
def overview():
    return render_template('overview.html')


@app.route('/messages')
def messages():
    return render_template('messages.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/groups')
def groups():
    return render_template('groups.html')


@app.route('/requests')
def requests():
    return render_template('requests.html')
@app.route('/discover')
def discover():
    return render_template('discover.html')


if __name__ == '__main__':
    app.run(debug=True)
