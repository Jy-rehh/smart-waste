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

def create_user_in_firestore(username, minutes):
    expiry = datetime.now() + timedelta(minutes=minutes)
    doc_ref = firestore_db.collection('Users Collection').document(username)
    doc_ref.set({
        'UserID': username,
        'WiFiTimeAvailable': minutes,
        'time_created': firestore.SERVER_TIMESTAMP,
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
        'start_time': start_time,
        'end_time': end_time,
        'wifi_minutes_used': 0,
        'device_mac': 'unknown'
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

    doc_ref = firestore_db.collection('Users Collection').document(username)
    print("→ Trying to fetch document from Firestore...")
    try:
        snapshot = doc_ref.get()
        print("→ Document fetched.")
        if snapshot.exists:
            print(f"[Warning] User '{username}' already exists in Firestore. Skipping.")
            return
    except Exception as e:
        print(f"[Error] Firestore fetch failed: {e}")
        return

    existing_user = realtime_db.child(username).get()
    if existing_user:
        print(f"[Warning] User '{username}' already exists in Realtime DB. Skipping.")
        return

    # Step 2: Skip MikroTik for now
    # create_hotspot_user(username, password=username + "_pass", time_minutes=minutes)

    print(f"[Step 3] Creating user in Firestore...")
    create_user_in_firestore(username, minutes)

    print(f"[Step 4] Creating user in Realtime DB...")
    create_user_in_realtime_db(username, minutes)

    print(f"[All Done] {username} created successfully with {minutes} minutes.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <minutes>")
        sys.exit(1)
    _, usr, mins = sys.argv
    main(usr, int(mins))
