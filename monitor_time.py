import time
import firebase_admin
from firebase_admin import credentials, firestore
from librouteros import connect

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
users_ref = db.collection('users')

# Function to connect to MikroTik
def connect_mikrotik():
    return connect(username='your_username', password='your_password', host='mikrotik_ip')

# Function to disconnect user from MikroTik HotSpot
def disconnect_user(user_id):
    api = connect_mikrotik()
    api('/ip/hotspot/user/remove', {'numbers': user_id})
    print(f"User {user_id} disconnected from Wi-Fi.")

# Function to check users' time remaining and disconnect if time expired
def monitor_users():
    while True:
        # Fetch all users from Firestore
        for user_doc in users_ref.stream():
            user_id = user_doc.id
            time_remaining = user_doc.to_dict().get('time_remaining', 0)
            
            if time_remaining <= 0:
                # If time is expired, disconnect user
                print(f"User {user_id}'s time expired. Disconnecting...")
                disconnect_user(user_id)
            else:
                # Decrease time remaining by 1 minute
                users_ref.document(user_id).update({'time_remaining': time_remaining - 1})
                print(f"User {user_id} has {time_remaining - 1} minutes remaining.")
        
        # Wait for 1 minute before checking again
        time.sleep(60)

if __name__ == "__main__":
    monitor_users()
