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

# Connect to MikroTik
def connect_mikrotik():
    print("Connecting to MikroTik router...")
    return connect(username='your_username', password='your_password', host='192.168.50.1', port=8728)

# Disable user on MikroTik Hotspot
def disable_user(username):
    print(f"Disabling user {username}...")
    try:
        api = connect_mikrotik()
        hotspot_users = api.path('ip', 'hotspot', 'user')
        
        # Find the user
        for user in hotspot_users.get():
            if user['name'] == username:
                hotspot_users.set(id=user['.id'], disabled='true')
                print(f"User {username} disabled.")
                return
        print(f"User {username} not found!")
    except Exception as e:
        print(f"Failed to disable user {username}: {e}")

# Enable user on MikroTik Hotspot
def enable_user(username):
    print(f"Enabling user {username}...")
    try:
        api = connect_mikrotik()
        hotspot_users = api.path('ip', 'hotspot', 'user')
        
        # Find the user
        for user in hotspot_users.get():
            if user['name'] == username:
                hotspot_users.set(id=user['.id'], disabled='false')
                print(f"User {username} enabled.")
                return
        print(f"User {username} not found!")
    except Exception as e:
        print(f"Failed to enable user {username}: {e}")

# Monitor users' time_remaining
def monitor_users():
    print("Starting user monitoring...")

    while True:
        print("Fetching users from Firestore...")
        users = list(users_ref.stream())

        if not users:
            print("No users found in Firestore.")
            break

        active_users = 0

        for user_doc in users:
            user_id = user_doc.id
            data = user_doc.to_dict()
            username = data.get('username')  # <-- use username
            time_remaining = data.get('time_remaining', 0)

            if username is None:
                print(f"User {user_id} missing username field. Skipping...")
                continue

            if time_remaining <= 0:
                print(f"User {username}'s time expired. Disabling...")
                disable_user(username)
            else:
                print(f"User {username} has {time_remaining} minutes left. Ensuring enabled...")
                enable_user(username)
                
                # Decrease time
                new_time = time_remaining - 1
                users_ref.document(user_id).update({'time_remaining': new_time})
                print(f"User {username} now has {new_time} minutes remaining.")
                active_users += 1

        if active_users == 0:
            print("All users have expired time. Stopping monitoring.")
            break

        print("Waiting 1 minute before next check...")
        time.sleep(60)

if __name__ == "__main__":
    print("Script is running...")
    monitor_users()
