import os
from curl_cffi import const
from supabase import create_client, Client
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
from flask import flash, redirect, url_for, Flask

window =tk.Tk()
window.wm_attributes('-topmost', 1)
window.withdraw()

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

def getAllUsers():
    try:
        response = supabase_admin.table('app_user').select("*").execute()
        return response.data
    except Exception as e:
        print("Error fetching users: ", e)
        return []

def getUserFriends(userid):
    try:
        friends = []
        response = supabase_admin.table('userfriends').select('*').execute()
        for i in response.data:
            if i['userid_1'] == userid or i['userid_2'] == userid: 
                if i['userid_1'] == userid:
                    i['userid_2'] = getUserProfile(i['userid_2'])
                    friends.append((i['userid_2']['name'], i['userid_2']['profile_image']))
                else:
                    i['userid_1'] = getUserProfile(i['userid_1'])
                    friends.append((i['userid_1']['name'], i['userid_1']['profile_image']))
        return friends
    except Exception as e:
        print("Error fetching friends: ", e)
        return []


def getUserProfile(userid):
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

def findUserProfile(test):
    
    try:
        response = supabase_admin.table('app_user').select("*").eq("userid", test).execute()
        if response.data:
            return response.data
        else:
            print("User not found")
            return None
    except Exception as e:
        test ='%' + test + '%'
        response = supabase_admin.table('app_user').select("*").ilike("name", test).execute()
        if response.data:
            return response.data
        else:
            print("User not found")
            return None

def uploadProfilePic(userid):
    file1 = filedialog.askopenfilename(
        title="Select File to Upload",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")]
    )
    try:
        with open(file1, "rb") as f:
            supabase.storage.from_("profile_images").upload(
                file=f,
                path=userid+'.png',
                file_options={"content-type":'png', "upsert": "true"}
            )
            return True
    
    except Exception as e:
        print("Error occured uploading the file", e)
        return False
"""
response = supabase.auth.sign_in_with_password({
            "email": "catherinegracelabrador@gmail.com",
            "password": 'test123456'
        })

print(findUserProfile("dummy"))

uploadProfilePic(response.user.id)
"""