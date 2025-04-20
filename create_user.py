import sys
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore, db
# from mikrotik_api import create_hotspot_user  # Temporarily disable MikroTik

# ——— Initialize Firebase ———
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-waste-smart-access-a425c-default-rtdb.firebaseio.com/'
})

firestore_db = firestore.client()  # Firestore client
realtime_db = db.reference('users')  # Realtime DB reference at /users

def update_user_in_firestore(username, minutes):
    # Get the existing document
    doc_ref = firestore_db.collection('Users Collection').document(username)
    snapshot = doc_ref.get()
    
    if snapshot.exists:
        # User exists, update WiFiTimeAvailable and time_expiry
        user_data = snapshot.to_dict()
        new_time_available = user_data['WiFiTimeAvailable'] + minutes  # Add new time
        new_expiry = datetime.now() + timedelta(minutes=new_time_available)
        
        doc_ref.update({
            'WiFiTimeAvailable': new_time_available,
            'time_expiry': new_expiry
        })
        print(f"[Firestore] Updated {username} with additional {minutes} minutes, new expiry: {new_expiry}")
    else:
        # User does not exist, create new
        create_user_in_firestore(username, minutes)

def update_user_in_realtime_db(username, minutes):
    # Get the current data in Realtime DB
    user_ref = realtime_db.child(username)
    existing_user_data = user_ref.get()

    if existing_user_data:
        # User exists, update the end_time and wifi_minutes_used
        current_end_time = existing_user_data['end_time']
        current_wifi_minutes_used = existing_user_data['wifi_minutes_used']
        
        # Calculate new end_time and total minutes used
        start_time = datetime.now().isoformat()
        new_end_time = (datetime.fromisoformat(current_end_time) + timedelta(minutes=minutes)).isoformat()

        user_ref.update({
            'end_time': new_end_time,
            'wifi_minutes_used': current_wifi_minutes_used + minutes
        })
        print(f"[Realtime DB] Updated {username} with additional {minutes} minutes, new end time: {new_end_time}")
    else:
        # User does not exist, create new
        create_user_in_realtime_db(username, minutes)

def create_user_in_firestore(username, minutes):
    expiry = datetime.now() + timedelta(minutes=minutes)
    doc_ref = firestore_db.collection('Users Collection').document(username)
    doc_ref.set({
        'UserID': username,
        'WiFiTimeAvailable': minutes,
        'time_expiry': expiry,
        'status': 'active',
        'username': username,
        'password': username + "_pass"
    })
    print(f"[Firestore] {username} added with {minutes} minutes at {expiry}")  # Debug print

def create_user_in_realtime_db(username, minutes):
    now = datetime.now()
    start_time = now.isoformat()
    end_time = (now + timedelta(minutes=minutes)).isoformat()

    user_data = {
        'user_id': username,
        'status': 'active',
        'username': username,
        'wifi_minutes_used': 0,
        'start_time': start_time,
        'end_time': end_time,
    }

    # Check if user already exists
    existing_user = realtime_db.child(username).get()
    if existing_user:
        print(f"[Warning] User '{username}' already exists in Realtime DB. Skipping.")
        return

    realtime_db.child(username).set(user_data)
    print(f"[Realtime DB] {username} created with Wi-Fi time: {minutes} minutes, from {start_time} to {end_time}.")  # Debug print


def main(username: str, minutes: int):
    print(f"[Step 1] Checking if user '{username}' exists...")

    # Check Firestore first
    print("→ Trying to fetch document from Firestore...")
    doc_ref = firestore_db.collection('Users Collection').document(username)
    try:
        snapshot = doc_ref.get()
        print("→ Document fetched.")
        if snapshot.exists:
            print(f"[Info] User '{username}' exists in Firestore. Updating Wi-Fi time...")
            update_user_in_firestore(username, minutes)
            return
    except Exception as e:
        print(f"[Error] Firestore fetch failed: {e}")
        return

    # Check Realtime DB
    existing_user = realtime_db.child(username).get()
    if existing_user:
        print(f"[Info] User '{username}' exists in Realtime DB. Updating Wi-Fi time...")
        update_user_in_realtime_db(username, minutes)
        return

    # If not found, create the user
    print(f"[Step 3] Creating user in Firestore...")
    create_user_in_firestore(username, minutes)

    print(f"[Step 4] Creating user in Realtime DB...")
    create_user_in_realtime_db(username, minutes)

    print(f"[All Done] {username} created/updated successfully with {minutes} minutes.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <minutes>")
        sys.exit(1)
    _, usr, mins = sys.argv
    main(usr, int(mins))
