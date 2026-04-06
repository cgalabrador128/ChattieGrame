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


@app.route('/profile/<userid>', methods =['GET', 'POST'])
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


@app.route('/groups', methods=['GET', 'POST'])
def groups():
    if request.method == 'POST':
        if request.form['group-name']:
            groupName = request.form.get('group-name')
            if not groupName:
                return redirect(url_for('groups'))
            id = dat.createGroup(groupName, session.get('userid'))
            members = dat.getGroupMembers(id)
            groupinfo = dat.getGroup(id)
            return redirect(url_for('view_group', groupid = str(id)), members=members, groupinfo = groupinfo)
        return redirect(url_for('groups'))
    groups = dat.getUserGroups(session.get('userid'))
    return render_template('groups.html', groups=groups)


@app.route('/view-group/<groupid>')
def view_group(groupid):
    try:
        session["currentgroup"]= groupid
        groupMembers = dat.getGroupMembers(groupid)
        groupinfo = dat.getGroup(groupid)
        return render_template('view-group.html', members = groupMembers, groupinfo = groupinfo)
    except Exception as e:
        print("Error loading data ", e)
    return render_template('view-group.html', members=None)


@app.route('/requests')
def requests():
    return render_template('requests.html')


@app.route('/discover', methods=['GET','POST'])
def discover():
    if request.method == 'POST':
        query = request.form.get('query')
        users = dat.findUserProfile(query)
        return render_template('discover.html', users=users)
    users = dat.getAllUsers()
    return render_template('discover.html', users=users)

@app.route('/d_Func/<func>', methods=['GET','POST'])
def definedFunc(func):
    if func == "profile_upload":
        return dat.uploadProfilePic(session.get('userid'))
      
    elif func == "add_member_button":
        return dat.joinGroupviaInvite()
        #unfinished(1)
    return ""

@app.route('/remove_member/<userid>', methods=['POST'])
def remove_member(userid):
    return dat.removeMember(userid)
if __name__ == '__main__':
    app.run(debug=True)
