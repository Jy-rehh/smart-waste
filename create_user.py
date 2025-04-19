# create_user.py

import sys
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from mikrotik_api import create_hotspot_user

# ——— Initialize Firebase ———
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


def main(username: str, minutes: int):
    password = username + "_pass"     # or generate however you like
    # 1) Spin up user on MikroTik
    create_hotspot_user(username, password=password, time_minutes=minutes)

    # 2) Log to Firestore
    expiry = datetime.now() + timedelta(minutes=minutes)
    db.collection('hotspot_users').document(username).set({
        'username': username,
        'password': password,
        'time_created': firestore.SERVER_TIMESTAMP,
        'time_expiry': expiry,
        'status': 'active'
    })
    print(f"[Firebase] {username} expires at {expiry}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <minutes>")
        sys.exit(1)
    _, usr, mins = sys.argv
    main(usr, int(mins))
