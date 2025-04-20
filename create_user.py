# create_user.py

import sys
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from mikrotik_api import create_hotspot_user

# ——— Initialize Firebase ———
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def main(username: str, minutes: int):
    password = username + "_pass"  # generate password logic

    # Check if user already exists in Firestore
    doc_ref = db.collection('Users Collection').document(username)
    if doc_ref.get().exists:
        print(f"[Warning] User '{username}' already exists in Firestore. Skipping creation.")
        return

    # 1) Spin up user on MikroTik
    create_hotspot_user(username, password=password, time_minutes=minutes)

    # 2) Log to Firestore inside "Users Collection"
    expiry = datetime.now() + timedelta(minutes=minutes)

    doc_ref.set({
        'Email': '',
        'Name': '',
        'LoyaltyPoints': 0,
        'RewardPoints': 0,
        'TotalBottlesDeposited': 0,
        'UserID': username,
        'WiFiTimeAvailable': minutes,
        'time_created': firestore.SERVER_TIMESTAMP,
        'time_expiry': expiry,
        'status': 'active',
        'username': username,
        'password': password
    })

    print(f"[Firebase] {username} added to Users Collection. Expires at {expiry}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <minutes>")
        sys.exit(1)
    _, usr, mins = sys.argv
    main(usr, int(mins))
