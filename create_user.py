# create_user.py

import sys
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore, db
from mikrotik_api import create_hotspot_user

# ——— Initialize Firebase ———
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-waste-smart-access-a425c-default-rtdb.firebaseio.com/'  # Replace with your URL
})

firestore_db = firestore.client()  # Firestore client
realtime_db = db.reference('users')  # Realtime Database reference for users

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
    print(f"[Firestore] {username} added with {minutes} minutes")

def create_user_in_realtime_db(username, minutes):
    now = datetime.now()
    start_time = now.isoformat()  # Convert start time to ISO format
    end_time = (now + timedelta(minutes=minutes)).isoformat()  # Calculate end time based on Wi-Fi minutes

    user_data = {
        'user_id': username,
        'status': 'active',
        'start_time': start_time,
        'end_time': end_time,
        'wifi_minutes_used': 0,  # Initially, no Wi-Fi time used
        'device_mac': 'unknown'  # Device MAC can be updated later
    }

    # Check if user already exists in Realtime Database
    existing_user = realtime_db.child(username).get()
    if existing_user:
        print(f"[Warning] User '{username}' already exists in Realtime Database. Skipping.")
        return

    ref = realtime_db.child(username)
    ref.set(user_data)
    print(f"[Realtime DB] {username} created with Wi-Fi time: {minutes} minutes.")

def main(username: str, minutes: int):
    # Check if user exists in Firestore
    doc_ref = firestore_db.collection('Users Collection').document(username)
    if doc_ref.get().exists:
        print(f"[Warning] User '{username}' already exists in Firestore. Skipping creation.")
        return

    # Check if user exists in Realtime Database
    existing_user = realtime_db.child(username).get()
    if existing_user:
        print(f"[Warning] User '{username}' already exists in Realtime Database. Skipping creation.")
        return

    # 1) Create user in MikroTik
    create_hotspot_user(username, password=username + "_pass", time_minutes=minutes)

    # 2) Create user in Firestore
    create_user_in_firestore(username, minutes)

    # 3) Create user in Realtime Database
    create_user_in_realtime_db(username, minutes)

    print(f"[All] {username} created successfully with {minutes} minutes.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <minutes>")
        sys.exit(1)
    _, usr, mins = sys.argv
    main(usr, int(mins))
