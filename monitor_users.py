import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from mikrotik_api import disconnect_hotspot_user
import logging

# Firebase initialization
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Set up logging
logging.basicConfig(filename='disconnect_users.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def disconnect_expired_users():
    users_ref = db.collection("Users Collection")
    users = users_ref.stream()

    now = datetime.utcnow()
    for user in users:
        data = user.to_dict()
        expires_at = data.get("expires_at")
        if expires_at:
            exp_time = expires_at.replace(tzinfo=None)  # Remove timezone info if it exists
            if now > exp_time:
                logging.info(f"Disconnecting user: {user.id}")
                print(f"Disconnecting {user.id}")

                # Disconnect user from MikroTik
                disconnect_hotspot_user(user.id)  # ID should match MikroTik username

                # Update WiFiTimeAvailable and status
                users_ref.document(user.id).update({
                    "WiFiTimeAvailable": 0,
                    "status": "disconnected",  # Mark the user as disconnected
                    "disconnected_at": firestore.SERVER_TIMESTAMP  # Optional: log the time of disconnection
                })
                logging.info(f"User {user.id} disconnected and updated in Firebase.")

if __name__ == "__main__":
    disconnect_expired_users()
