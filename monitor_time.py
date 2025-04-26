import time
import firebase_admin
from firebase_admin import credentials, firestore
from librouteros import connect

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
users_ref = db.collection('Users Collection')

# Function to connect to MikroTik
def connect_mikrotik():
    print("Connecting to MikroTik router...")
    return connect(username='your_username', password='your_password', host='mikrotik_ip')

# Function to get currently active users from MikroTik
def get_active_users(api):
    active_users = {}
    try:
        active_sessions = api('/ip/hotspot/active/print')
        for session in active_sessions:
            user = session.get('user')
            session_id = session.get('.id')
            if user and session_id:
                active_users[user] = session_id
    except Exception as e:
        print(f"Failed to fetch active users: {e}")
    return active_users

# Function to disconnect an active user from MikroTik
def disconnect_user(api, session_id):
    try:
        api('/ip/hotspot/active/remove', {'numbers': session_id})
        print(f"Disconnected session {session_id}.")
    except Exception as e:
        print(f"Failed to disconnect session {session_id}: {e}")

# Function to monitor users
def monitor_users():
    print("Starting user monitoring...")
    
    while True:
        print("Fetching users from Firestore...")
        users = list(users_ref.stream())
        
        if not users:
            print("No users found.")
            break

        api = connect_mikrotik()
        active_sessions = get_active_users(api)

        active_users_count = 0

        for user_doc in users:
            user_id = user_doc.id
            data = user_doc.to_dict()
            time_remaining = data.get('time_remaining', 0)

            if user_id in active_sessions:
                # User is currently active
                if time_remaining <= 0:
                    print(f"User {user_id}'s time expired. Disconnecting...")
                    disconnect_user(api, active_sessions[user_id])
                else:
                    new_time = time_remaining - 1
                    users_ref.document(user_id).update({'time_remaining': new_time})
                    print(f"User {user_id} is active. Time remaining: {new_time} minutes.")
                    active_users_count += 1
            else:
                print(f"User {user_id} is not active. No time deducted.")

        if active_users_count == 0:
            print("No active users with remaining time. Stopping monitor.")
            break

        print("Waiting for 1 minute before next check...")
        time.sleep(60)

if __name__ == "__main__":
    print("Script is running...")
    monitor_users()
