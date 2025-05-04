import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import db as realtime_db  # Avoid naming conflict
from librouteros import connect
from datetime import datetime
import time

# ——— Initialize Firebase Admin with Firestore ———
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-waste-c39ac-default-rtdb.firebaseio.com/'
})
db = firestore.client()

# ——— Connect to MikroTik Router ———
try:
    api = connect(username='admin', password='', host='192.168.50.1')
    print("[*] Connected to MikroTik Router.")
except Exception as e:
    print(f"[!] Connection failed: {e}")
    exit()

# ——— Track already added MAC addresses ———
known_macs = set()

# ——— Continuous Monitoring Loop ———
while True:
    try:
        mac_addresses = []

        # Try fetching active users first
        active_users = list(api.path('ip', 'hotspot', 'active'))
        if active_users:
            #print("[*] Found active hotspot users.")
            mac_addresses = [user['mac-address'] for user in active_users]
        else:
            #print("[*] No active users. Trying hotspot hosts...")
            hosts = list(api.path('ip', 'hotspot', 'host'))
            mac_addresses = [user['mac-address'] for user in hosts]

        if not mac_addresses:
            print("[!] No MAC addresses found.")
        else:
            for user in active_users if active_users else hosts:
                mac = user['mac-address']
                ip = user.get('address', '')  # Safely get IP address, empty if not found

                # Check if user is already in the Firestore database
                doc_ref = db.collection('Users Collection').document(mac)
                doc = doc_ref.get()
                
                if not doc.exists:
                    #print(f"[-] MAC {mac} already exists in Firestore. No changes made.")
                #else:
                    # Add user to Firestore if not already present
                    doc_ref.set({
                        'UserID': mac,
                        'macAddress': mac,
                        'ipAddress': ip,
                        'status': "active",
                    })
                    known_macs.add(mac)
                    # Realtime DB path: /users/{mac_address_sanitized}
                    mac_sanitized = mac.replace(":", "-")  # Firebase Realtime DB keys cannot contain ":"

                    user_realtime_ref = realtime_db.reference(f'users/{mac_sanitized}')
                    user_realtime_ref.set({
                        'UserID': mac,
                        'WiFiTimeAvailable': 0,
                        'TotalBottlesDeposited': 0,
                        'DoneClicked': False,
                        'Counting': False,
                        'EndTime': None 
                    })

                    #print(f"[+] Added MAC: {mac}, IP: {ip} to Firestore.")

    except Exception as e:
        print(f"[!] Error while retrieving users: {e}")

    time.sleep(5) 
