import time
import firebase_admin
from firebase_admin import credentials, firestore
from librouteros import connect

# Initialize Firebase Admin SDK
# This sets up the connection to Firebase using your service account credentials
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)

# Firestore client
# This allows interaction with the Firestore database to fetch user data
db = firestore.client()
users_ref = db.collection('Users Collection')  # Access the 'users' collection in Firestore

# Function to connect to MikroTik
# This function establishes a connection to the MikroTik router
def connect_mikrotik():
    print("Connecting to MikroTik router...")
    return connect(username='your_username', password='your_password', host='mikrotik_ip')

# Function to disconnect user from MikroTik HotSpot
# This function removes a user from the MikroTik hotspot when their time expires
def disconnect_user(user_id):
    print(f"Attempting to disconnect user {user_id}...")
    api = connect_mikrotik()  # Connect to MikroTik router
    api('/ip/hotspot/user/remove', {'numbers': user_id})  # Remove user from hotspot
    print(f"User {user_id} disconnected from Wi-Fi.")  # Print confirmation

# Function to check users' time remaining and disconnect if time expired
# This function continuously checks users' remaining time and disconnects them when time is up
def monitor_users():
    print("Starting user monitoring...")
    while True:
        # Fetch all users from Firestore
        print("Fetching users from Firestore...")
        for user_doc in users_ref.stream():
            user_id = user_doc.id  # Get user ID
            time_remaining = user_doc.to_dict().get('time_remaining', 0)  # Get remaining time from Firestore
            
            # Check if time has expired
            if time_remaining <= 0:
                # If time is expired, disconnect user
                print(f"User {user_id}'s time expired. Disconnecting...")
                disconnect_user(user_id)  # Disconnect user from Wi-Fi
            else:
                # If time is still available, decrease time by 1 minute
                users_ref.document(user_id).update({'time_remaining': time_remaining - 1})
                print(f"User {user_id} has {time_remaining - 1} minutes remaining.")  # Print remaining time
        
        # Wait for 1 minute before checking again
        print("Waiting for 1 minute before checking again...")
        time.sleep(60)

if __name__ == "__main__":
    print("Script is running...")
    monitor_users()  # Start monitoring users' time and disconnecting when necessary
