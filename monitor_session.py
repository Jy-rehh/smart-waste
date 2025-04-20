import time
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from mikrotik_api import disconnect_hotspot_user  # You'll add this to disconnect users

# Initialize Firebase
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Configure logging for better monitoring
logging.basicConfig(filename='monitor_sessions.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def check_and_disconnect():
    now = datetime.now()
    try:
        # Query the users whose session has expired and status is active
        docs = db.collection('hotspot_users')\
                 .where('status', '==', 'active')\
                 .where('time_expiry', '<=', now)\
                 .stream()

        for doc in docs:
            user = doc.id
            print(f"[Monitor] Expired: {user}")
            logging.info(f"Expired session detected for user: {user}")

            # Disconnect user from MikroTik
            disconnect_hotspot_user(user)

            # Update Firestore: Set user status to disconnected
            db.collection('hotspot_users').document(user).update({
                'status': 'disconnected',
                'disconnected_at': firestore.SERVER_TIMESTAMP
            })

            print(f"[Firebase] Marked {user} disconnected")
            logging.info(f"User {user} disconnected and status updated in Firebase.")

    except firebase_admin.exceptions.FirebaseError as e:
        logging.error(f"Firebase error occurred: {e}")
        print(f"[Error] Firebase error: {e}")
    except Exception as e:
        logging.error(f"General error occurred: {e}")
        print(f"[Error] General error: {e}")

if __name__ == "__main__":
    while True:
        try:
            check_and_disconnect()
        except Exception as e:
            logging.error(f"Unexpected error in monitor loop: {e}")
            print(f"[Error] Unexpected error: {e}")
        time.sleep(60)  # Wait 1 minute before next check (adjust based on your system's needs)
