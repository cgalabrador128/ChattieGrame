import os
from curl_cffi import const
from supabase import create_client, Client
from dotenv import load_dotenv
from flask import flash, redirect, url_for, Flask

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
            user_data_response = supabase.table('app_user').select("userid").eq("userid", response.user.id).execute()
            #return response.user
            print(user_data_response.data[0]['userid'])
            return user_data_response.data[0]['userid']
        
    except Exception as e:
        print("Login failed with error: ", e)
        return None

def getAllUsers():
    try:
        response = supabase_admin.table('app_user').select("*").execute()
        for user in response.data:
            if user['profile_image'] is None:
                # Add a default profile image URL
                user['profile_image'] = "https://t3.ftcdn.net/jpg/00/64/67/80/360_F_64678017_zUpiZFjj04cnLri7oADnyMH0XBYyQghG.jpg"
            else:
                user['profile_image'] = f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/profile_images/{user['userid']}.{user['profile_image']}"
        return response.data
    except Exception as e:
        print("Error fetching users: ", e)
        return []