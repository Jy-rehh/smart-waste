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
    # Use the correct IP address of MikroTik router
    return connect(username='your_username', password='your_password', host='192.168.50.1', port=8728)

# Function to disconnect user from MikroTik HotSpot
def disconnect_user(user_id):
    print(f"Attempting to disconnect user {user_id}...")
    try:
        api = connect_mikrotik()  # Connect to MikroTik router
        # Remove user from hotspot
        api('/ip/hotspot/user/remove', {'numbers': user_id})
        print(f"User {user_id} disconnected from Wi-Fi.")
    except Exception as e:
        print(f"Failed to disconnect user {user_id}: {e}")

# Function to re-enable user for internet access
def reconnect_user(user_id):
    print(f"Attempting to reconnect user {user_id}...")
    try:
        api = connect_mikrotik()  # Connect to MikroTik router
        # Add the user back to the hotspot to allow internet access
        api('/ip/hotspot/user/add', {'name': user_id, 'profile': 'default'})  # Ensure 'profile' matches your configuration
        print(f"User {user_id} reconnected to Wi-Fi.")
    except Exception as e:
        print(f"Failed to reconnect user {user_id}: {e}")

# Function to check users' time remaining and disconnect if time expired
def monitor_users():
    print("Starting user monitoring...")
    
    while True:
        print("Fetching users from Firestore...")
        users = list(users_ref.stream())  # Fetch all users once
        
        if not users:
            print("No users found in Firestore.")
            break

        active_users = 0  # Counter for users who still have time left

        for user_doc in users:
            user_id = user_doc.id
            data = user_doc.to_dict()
            time_remaining = data.get('time_remaining', 0)

            if time_remaining <= 0:
                print(f"User {user_id}'s time expired. Disconnecting...")
                disconnect_user(user_id)
            else:
                new_time = time_remaining - 1
                users_ref.document(user_id).update({'time_remaining': new_time})
                print(f"User {user_id} has {new_time} minutes remaining.")
                active_users += 1  # There are still active users
                
                # Reconnect user if they have time remaining
                reconnect_user(user_id)

        if active_users == 0:
            print("All users have expired their time. Stopping monitoring.")
            break  # Exit the loop if no users have time left

        print("Waiting for 1 minute before next check...")
        time.sleep(60)

if __name__ == "__main__":
    print("Script is running...")
    monitor_users()
