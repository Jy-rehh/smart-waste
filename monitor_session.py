import time
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, db
from mikrotik_api import disconnect_hotspot_user  # You'll add this to disconnect users

# Initialize Firebase
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)
firestore_db = firestore.client()
realtime_db = db.reference('users')  # Reference to Realtime DB

# Configure logging for better monitoring
logging.basicConfig(filename='monitor_sessions.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def check_and_disconnect():
    now = datetime.now()
    try:
        # Query the users whose session has expired and status is active
        docs = firestore_db.collection('hotspot_users')\
                 .where('status', '==', 'active')\
                 .where('time_expiry', '<=', now)\
                 .stream()

        for doc in docs:
            user = doc.id
            print(f"[Monitor] Expired: {user}")
            logging.info(f"Expired session detected for user: {user}")

            # Disconnect user from MikroTik
            disconnect_hotspot_user(user)

            # Fetch user's session data from Realtime DB
            user_data = realtime_db.child(user).get()

            if user_data.val():
                wifi_time_available = user_data.val().get('wifi_minutes_available', 0)
                wifi_minutes_used = user_data.val().get('wifi_minutes_used', 0)

                # If the Wi-Fi time has been used up, set status to disconnected
                if wifi_time_available <= wifi_minutes_used:
                    # Update the user's status to disconnected in Firestore
                    firestore_db.collection('hotspot_users').document(user).update({
                        'status': 'disconnected',
                        'disconnected_at': firestore.SERVER_TIMESTAMP
                    })

                    print(f"[Firebase] Marked {user} disconnected in Firestore.")
                    logging.info(f"User {user} disconnected and status updated in Firestore.")
                    
                    # Optionally, update the user's Realtime DB entry to reflect status change
                    realtime_db.child(user).update({
                        'status': 'disconnected',
                        'wifi_minutes_used': wifi_minutes_used
                    })
                    logging.info(f"User {user} marked as disconnected in Realtime DB.")
            else:
                # If user is not found in Realtime DB, create them
                user_doc = firestore_db.collection('hotspot_users').document(user).get()
                if user_doc.exists:
                    user_info = user_doc.to_dict()
                    wifi_time_available = user_info.get('WiFiTimeAvailable', 0)
                    start_time = datetime.now().isoformat()
                    end_time = (datetime.now() + timedelta(minutes=wifi_time_available)).isoformat()

                    # Create user in Realtime DB
                    user_data = {
                        'user_id': user,
                        'status': 'active',
                        'wifi_minutes_available': wifi_time_available,
                        'wifi_minutes_used': 0,
                        'start_time': start_time,
                        'end_time': end_time,
                        'device_mac': 'unknown'
                    }
                    realtime_db.child(user).set(user_data)
                    print(f"[Realtime DB] {user} created in Realtime DB with Wi-Fi time: {wifi_time_available} minutes.")
                    logging.info(f"User {user} created in Realtime DB with Wi-Fi time: {wifi_time_available} minutes.")
                    
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
