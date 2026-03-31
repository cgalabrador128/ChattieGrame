from flask import Flask, flash, session, render_template, request, redirect, url_for
import data as dat
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if session.get('userid') is not None:
            return redirect(url_for('overview'))
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            data = dat.loginUser(email, password)
            session['userid'] = data.id
            session.permanent = True

            if email and password and session.get('userid') is not None:
                flash('Login successful!')
                return redirect(url_for('overview'))

            else:
                error = "Invalid email or password. Please try again."
                return render_template('login.html', error=error)
        return render_template('login.html')
        
    except Exception as e:
        print("Error during login: ", e)
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if session.get('userid') is not None:
            return redirect(url_for('overview'))
        else:
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
    except Exception as e:
        print("Error during signup: ", e)
        return render_template('signup.html')


@app.route('/overview')
def overview():
    return render_template('overview.html')


@app.route('/messages')
def messages():
    return render_template('messages.html')


@app.route('/profile/<userid>')
def profile(userid):
    try:
        if session.get('userid') is None:
            friends = dat.getUserFriends(session.get('userid'))
            profile = dat.getUserProfile(session.get('userid'))
            return render_template('profile.html', user=session.get('userid'), friends=friends, profile=profile)
        else:
            friends = dat.getUserFriends(userid)
            profile = dat.getUserProfile(userid)
            return render_template('profile.html', user=userid, friends=friends, profile=profile)
    except Exception as e:
        print("Error fetching profile: ", e)
        return render_template('profile.html', user=session.get('userid'), friends=[], profile=None)

@app.route('/groups')
def groups():
    return render_template('groups.html')


@app.route('/requests')
def requests():
    return render_template('requests.html')

@app.route('/discover')
def discover():
    users = dat.getAllUsers()
    return render_template('discover.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)
