import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from mikrotik_api import disconnect_hotspot_user

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def disconnect_expired_users():
    users_ref = db.collection("Users Collection")
    users = users_ref.stream()

    now = datetime.utcnow()
    for user in users:
        data = user.to_dict()
        expires_at = data.get("expires_at")
        if expires_at:
            exp_time = expires_at.replace(tzinfo=None)
            if now > exp_time:
                print(f"Disconnecting {user.id}")
                disconnect_hotspot_user(user.id)  # ID should match MikroTik username
                users_ref.document(user.id).update({"WiFiTimeAvailable": 0})

if __name__ == "__main__":
    disconnect_expired_users()
