import sys
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from mikrotik_api import create_hotspot_user
import random
import string

# ——— Initialize Firebase ———
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to generate a random secure password
def generate_secure_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def main(username: str, minutes: int):
    # Generate a secure password
    password = generate_secure_password()  # Use a random password generator for better security

    # Check if user already exists in Firestore
    doc_ref = db.collection('Users Collection').document(username)
    if doc_ref.get().exists:
        print(f"[Warning] User '{username}' already exists in Firestore. Skipping creation.")
        return

    try:
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

    except Exception as e:
        print(f"[Error] Failed to create user '{username}': {str(e)}")
        return

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <minutes>")
        sys.exit(1)
    _, usr, mins = sys.argv
    main(usr, int(mins))
