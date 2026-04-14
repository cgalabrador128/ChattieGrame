import os
from datetime import datetime as dt
from datetime import timezone
from curl_cffi import const
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
from flask import flash, redirect, url_for, Flask, request, jsonify
import randomlibrary as randlib
from json import dumps

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_MB = 5

load_dotenv()
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_PUBLISHABLE_KEY")
)
supabase_anon: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_ANON_KEY")
)
supabase_admin: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)


def signupUser(name, email, password):
    try:
        # Create auth user
        response = supabase.auth.sign_up({"email": email, "password": password})

        if response.user:
            user_id = response.user.id

            # Insert user profile using service role (server operation)
            supabase_admin.table('app_user').insert({
                "userid": user_id,
                "name": name,
                "email": email
            }).execute()

            # Insert credentials using service role
            supabase_admin.table('user_cred').insert({
                "userid": user_id,
                "password": password
            }).execute()

            print("Signup successful! Please check your email.")
            return True
        else:
            print("Signup failed: No user returned")
            return False

    except Exception as e:
        print("Signup failed with error: ", e)
        return False


def loginUser(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.user:
            print("Login successful.")
            return response.user

    except Exception as e:
        print("Login failed with error: ", e)
        return None

def getAllUsers(): #returns all users for discover html
    try:
        response = supabase_admin.table('app_user').select("*").execute()
        return response.data
    except Exception as e:
        print("Error fetching users: ", e)
        return []

def getUserFriends(userid): #returns all user friends depending on the userid
    try:
        friends = []
        response = supabase_admin.table('userfriends').select('*').execute()
        for i in response.data:
            if i['userid_1'] == userid or i['userid_2'] == userid:
                if i['userid_1'] == userid:
                    i['userid_2'] = getUserProfile(i['userid_2'])
                    friends.append((i['userid_2']['name'], i['userid_2']['profile_image'], i['userid_2']['userid']))
                else:
                    i['userid_1'] = getUserProfile(i['userid_1'])
                    friends.append((i['userid_1']['name'], i['userid_1']['profile_image'], i['userid_1']['userid']))
        return friends
    except Exception as e:
        print("Error fetching friends: ", e)
        return []

def getUserProfile(userid): # gets userprofile depending on the userid only
    try:
        response = supabase_admin.table('app_user').select("*").eq("userid", userid).execute()
        if response.data:
            user = response.data[0]
            return user
        else:
            print("User not found")
            return None
    except Exception as e:
        print("Error fetching user profile: ", e)
        return None

def findUserProfile(searchData): # finds userprofile based on userid/name

    try:
        response = supabase_admin.table('app_user').select("*").eq("userid", searchData).execute()
        if response.data:
            return response.data
        else:
            print("User not found")
            return None
    except Exception as e:
        searchData ='%' + searchData + '%'
        response = supabase_admin.table('app_user').select("*").ilike("name", searchData).execute()
        if response.data:
            return response.data
        else:
            print("User not found")
            return None

def uploadProfilePic(userid): #uploads profile picture
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        try:
            supabase.storage.from_("profile_images").remove([f"{userid}{ext}"])
        except:
            pass

    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Validate MIME type
    if file.content_type not in ALLOWED_TYPES:
        return jsonify({"error": "Only image files are allowed"}), 400

    # Read and validate size
    file_bytes = file.read()
    if len(file_bytes) > MAX_SIZE_MB * 1024 * 1024:
        return jsonify({"error": f"File exceeds {MAX_SIZE_MB}MB limit"}), 400

    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    unique_name = f"{userid}{ext}"

    # Upload to Supabase
    supabase.storage.from_("profile_images").upload(
        path=unique_name,
        file=file_bytes,
        file_options={"content-type": file.content_type, "upsert": "true" }
    )

    public_url = supabase.storage.from_("profile_images").get_public_url(unique_name)
    supabase_admin.table("app_user").update({"profile_image":public_url}).eq("userid", userid).execute()

    return jsonify({"url": public_url}), 200

def createGroup(name, userid):
    try:
        response = supabase_admin.table('groupie').insert({"name": name, "membercount":1}).execute()
        groupid = response.data[0]['groupid']

        supabase_admin.table('usergroups').insert({"userid":userid, "groupid":groupid, "role":"OWNER"}).execute()
        return groupid
    except Exception as e:
        print("Error retrieving data", e)
        return None

def joinGroupviaInvite(groupid, userid):
    try:
        response = supabase_admin.table('groupie').select("membercount").eq("groupid", groupid).single().execute()
        membercount = response.data['membercount'] + 1

        #update values
        supabase_admin.table('usergroups').insert({"userid":userid, "groupid":groupid}).execute()
        supabase_admin.table('groupie').update({"membercount":membercount}).eq('groupid', groupid).execute()
    except Exception as e:
        print("Error updating data", e)

def joinGroupviaCode(inv_code, userid):
    try:
        response = supabase_admin.table('groupie').select('groupid').eq('inv_code', inv_code).single().execute()
        if response.data:
            joinGroupviaInvite(response.data['groupid'], userid)
        else:
            print("No groups with that code")
    except Exception as e:
        print("Error:", e)

def generateGroupCode(groupid):
    try:
        code = None
        while True:
            code = randlib.generate_code()
            response = supabase_admin.table('groupie').select("inv_code").eq('inv_code', code).single().execute()
            if not response.data:
                break
        response = supabase_admin.table('groupie').select('*').eq('groupid', groupid).execute()
        if response.data:
            supabase_admin.table('groupie').update({'inv_code': code, 'created_at':randlib.nowtime()}).eq('groupid', groupid).execute()
    except Exception as e:
        print("Error:", e)

def getGroupMembers(groupid):
    try:
        response = supabase_admin.table('usergroups').select('*').eq('groupid', groupid).execute()
        if response.data:
            x =[]
            for i in response.data:
                r2 = supabase_admin.table('app_user').select("*").eq("userid", i['userid']).single().execute()
                r2.data['role']= i['role']
                x.append(r2.data)
            return x
        else:
            print("Group does not exist")
            return None
    except Exception as e:
        print("Error: ", e)
        return None

def getGroup(groupid):
    try:
        response = supabase_admin.table("groupie").select('*').eq('groupid', groupid).single().execute()
        return response.data
    except Exception as e:
        print(e)
        return None


def getUserGroups(userid):
    try:
        response = supabase.table('usergroups').select('groupid').eq('userid', userid).execute()
        if response.data:
            groups = []
            for r in response.data:
                t = supabase_admin.table("groupie").select('groupid, name, membercount').eq('groupid', r['groupid']).execute()
                groups.append(t.data[0])
            print(groups)
            return groups
        else:
            print("User has no groups")
            return None
    except Exception as e:
        print("Error occurred: ",e)
        return None

def removeMember(userid):
    try:
        supabase_admin.table('usergroups').delete().eq('userid', userid).execute()
    except Exception as e:
        print(e)

def generatechatBody(id1, id2): #create a message-prompt poop
    try:
        response = supabase_admin.table('conversation_details').insert({
            "created_at":randlib.nowtime()
        }).execute()
        supabase_admin.table('conversation_participants').insert({
            "chatid": response.data[0]["chatid"],
            'userid': id1
        }).execute()
        supabase_admin.table('conversation_participants').insert({
            "chatid": response.data[0]["chatid"],
            'userid': id2
        }).execute()
        return response.data[0]
    except Exception as e:
        print("error", e)
    
def getRecentChat(chatid):
    try:
        response = supabase_admin.table('chat').select('*').eq('chatid', id).order("created_at", desc=True).limit(1).execute()
        if response: 
            return response.data
        return None
    except Exception as e:
        print('err', e)
        return None
    
def getAllChat(userid): #preview sidebar messages
    try:
        responses = supabase.table('conversation_participants').select('*').eq('userid', userid).execute()
        chatsum = []
        for r in responses.data:
            id = r['chatid']
            valid = supabase_admin.table('chat').select('*').match({'userid_sender':userid,'chatid':id}).execute()
            if valid.data:
                respo = supabase_admin.table('chat').select("*").eq('chatid',id).order("created_at",desc=True).limit(1).execute()
                chatmateid = supabase_admin.table('conversation_participants').select('userid').neq('userid', userid).eq('chatid',id).single().execute()
                name = supabase_admin.table('app_user').select('name, profile_image').eq('userid', chatmateid.data['userid']).single().execute()
                mahtuple = (id, name.data, respo.data)
                chatsum.append(mahtuple)
        return chatsum
    except Exception as e:
        print("error", e)

def getAllRequests(userid):
    try:
        responses = supabase.table('conversation_participants').select('*').eq('userid', userid).execute()
        chatsum = []
        for r in responses.data:
            id = r['chatid']
            valid = supabase_admin.table('chat').select('*').match({'userid_sender':userid,'chatid':id}).execute()
            if valid.data:
                respo = supabase_admin.table('chat').select("*").eq('chatid',id).order("created_at",desc=True).limit(1).execute()
                chatmateid = supabase_admin.table('conversation_participants').select('userid').neq('userid', userid).eq('chatid',id).single().execute()
                name = supabase_admin.table('app_user').select('name, profile_image').eq('userid', chatmateid.data['userid']).single().execute()
                mahtuple = (id, name.data, respo.data)
                chatsum.append(mahtuple)
        return chatsum
    except Exception as e:
        print("error", e)

def getMessages(chatid):#get all messages for related chatid
    try:
        response = supabase_admin.table('chat').select("*").eq('chatid', chatid).order("created_at",desc=True).limit(50).execute()
        return response.data
    except Exception as e:
        print("error", e)

def sendMessage(chatid, senderid, chatdata): #send message to the user
    try:
        response = supabase.table('chat').insert({
            "chatid":chatid,
            "userid_sender":senderid,
            "chatcontent":chatdata,
            "created_at":randlib.nowtime(),
            "readstatus":False
        }).execute()
        return response.data
    except Exception as e:
        print("error", e)

def findExistingChat(userid, id2):
    try:
        response = supabase.table('conversation_participants').select('chatid').eq('userid',userid).execute()
        for r in response.data:
            found = supabase_admin.table('conversation_participants').select('chatid').eq('chatid',r['chatid']).eq('userid',id2).neq('userid',userid).execute()
            if found:
                print('Found!', found.data[0])
                return found.data[0]
        print ("No chat found")
        return False
    except Exception as e:
        print("Err", e)

def findChat(chatid):
    try:
        response = supabase_admin.table('conversation_details').select('*').eq('chatid', chatid).maybe_single().execute()
        if response:
            return True
        print('No chats found in this ID!')
        return False
    except Exception as e:
        print("err", e)

def findChatMate(chatid, userid):
    try:
        response = supabase_admin.table('conversation_participants').select('userid').eq('chatid',chatid).neq('userid',userid).maybe_single().execute()
        if response:
            return getUserProfile(response.data['userid'])
        print('none found')
        return None
    except Exception as e:
        print('err', e)
#loginUser('slyphyaubern@gmail.com', 'zxc123asd')
id1 ='44e71903-fbf6-4984-be17-caec8d5739a3' #Slyphy Aubern
id2 = '8313eebd-ee37-47e0-a086-ba3c5bc86a6c' #Catherine Labrador
id3 ='5d5d9f0c-172f-4888-9185-2a57b2210e31'# Gerome Carrot

x = '90626cdb-6a06-406d-bc46-3c8a085546b8'

"""
a = sendMessage(x, id1, "I'm sorry")
print(getMessages(x))
print( getAllChat(id1))

findExistingChat(id1, id3)
"""
#loginUser('catherinegracelabrador@gmail.com', 'test123456')
#print(getAllChat(id2))