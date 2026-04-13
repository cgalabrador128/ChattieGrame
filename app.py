from flask import Flask, flash, session, render_template, request, redirect, url_for,jsonify
from flask_socketio import SocketIO, emit
import os
import asyncio
from supabase import acreate_client, AsyncClient
import data as dat
from datetime import datetime
import uuid
import randomlibrary as rl

app = Flask(__name__)
sockio = SocketIO(app)
app.secret_key = str(uuid.uuid4())
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

async def supabase_listener():
    supabase: AsyncClient = await acreate_client(SUPABASE_URL, SUPABASE_KEY)

    def on_change(payload):
        #print("Change: ", payload)
        event_data = payload['data']
        if 'INSERT' in str(event_data['type']):
            new_row = event_data['record']
            message_content = new_row['chatcontent']
            sender_id = new_row['userid_sender']
            chatid = new_row['chatid']
            timestamp = new_row['created_at']
            sockio.emit('data_change', payload)

    channel = supabase.channel('chat_changes')
    await channel.on_postgres_changes(
        event="INSERT",
        schema="public",
        table="chat",
        callback=on_change
    ).subscribe()

    while True:
        await asyncio.sleep(1)


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


@app.route('/messages/<id>', methods=['GET', 'POST'])
def messages(id):
    preview = dat.getAllChat(session.get('userid'))
    if request.method == 'POST':
        message = request.json.get('message-content')
        if not message:
            return jsonify({"status": "error", "message": "No message content"}), 400
        dat.sendMessage(session.get('chatsession')[0], session.get('userid'), message)
        return jsonify({'status':'success'}), 200
    if preview == []:
        preview = None
    if id=='#':
        pass
    else:
        try:
            profile = []
            user1 = dat.getUserProfile(session.get('userid'))
            profile.append(user1)
            user = dat.getUserProfile(id)
            if user:
                print('IT RUNS')
                user2 = dat.getUserProfile(id)
                profile.append(user2)
            
            existing = dat.findExistingChat(session.get('userid'), id)
            existing2 = dat.findChat(id)
            if user and not existing and not existing2: 
                response = dat.generateinitialMessage(session.get("userid"), id)
                id = response["chatid"]
                session["chatsession"] = (id, preview, profile)
                return render_template('messages.html',id=id, preview=preview, profile=profile, messages = None)
            elif not existing and existing2:
                print('This runs')
                user2 = dat.findChatMate(id, session.get('userid'))
                profile.append(user2)
                session["chatsession"] = (id, preview, profile)
                response = dat.getMessages(id)
                return render_template('messages.html',id=id, preview=preview, profile=profile, messages = response)
            elif user and existing:
                id = existing['chatid']
                session["chatsession"] = (id, preview, profile)
                response = dat.getMessages(id)
                return render_template('messages.html',id=id, preview=preview, profile=profile, messages = response)
        except Exception as e:
            print("err", e)
    return render_template('messages.html', id=id, preview=preview, profile = None, messages = None)


@app.route('/profile/<userid>', methods =['GET', 'POST'])
def profile(userid):
    try:
        if 'userid' in session:
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
    return ""

@app.route('/remove_member/<userid>', methods=['POST'])
def remove_member(userid):
    return dat.removeMember(userid)

if __name__ == '__main__':
    sockio.start_background_task(lambda: asyncio.run(supabase_listener()))
    
    app.run(debug=True)
