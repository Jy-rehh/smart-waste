# monitor_sessions.py

import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from mikrotik_api import disconnect_hotspot_user  # you’ll add this

# ——— Initialize Firebase ———
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


def check_and_disconnect():
    now = datetime.now()
    docs = db.collection('hotspot_users')\
             .where('status', '==', 'active')\
             .where('time_expiry', '<=', now)\
             .stream()

    for doc in docs:
        user = doc.id
        print(f"[Monitor] Expired: {user}")
        disconnect_hotspot_user(user)

        db.collection('hotspot_users').document(user).update({
            'status': 'disconnected',
            'disconnected_at': firestore.SERVER_TIMESTAMP
        })
        print(f"[Firebase] Marked {user} disconnected")


if __name__ == "__main__":
    while True:
        try:
            check_and_disconnect()
        except Exception as e:
            print("Error in monitor loop:", e)
        time.sleep(10)  # wait 10 seconds before next check

