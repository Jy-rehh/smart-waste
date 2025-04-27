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

# Connect to MikroTik router
def connect_mikrotik():
    print("Connecting to MikroTik router...")
    return connect(username='admin', password='', host='192.168.50.1', port=8728)

# Disable user in MikroTik
def disable_user(username):
    try:
        api = connect_mikrotik()
        for user in api.path('/ip/hotspot/user'):
            if user.get('name') == username:
                api.path('/ip/hotspot/user').set(id=user['.id'], disabled='true')
                print(f"Disabled user {username}")
                return
        print(f"User {username} not found in MikroTik")
    except Exception as e:
        print(f"Error disabling user {username}: {e}")

# Enable user in MikroTik
def enable_user(username):
    try:
        api = connect_mikrotik()
        for user in api.path('/ip/hotspot/user'):
            if user.get('name') == username:
                api.path('/ip/hotspot/user').set(id=user['.id'], disabled='false')
                print(f"Enabled user {username}")
                return
        print(f"User {username} not found in MikroTik")
    except Exception as e:
        print(f"Error enabling user {username}: {e}")

# Monitor users
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
            username = data.get('username')  # make sure it's the email address
            time_remaining = data.get('time_remaining', 0)

            if time_remaining <= 0:
                print(f"User {username} time expired.")
                disable_user(username)
            else:
                new_time = time_remaining - 1
                users_ref.document(user_id).update({'time_remaining': new_time})
                print(f"User {username} has {new_time} minutes remaining.")
                enable_user(username)
                active_users += 1

        if active_users == 0:
            print("All users have expired their time. Stopping monitoring.")
            break

        print("Waiting for 1 minute...")
        time.sleep(60)

if __name__ == "__main__":
    monitor_users()
