import firebase_admin
from firebase_admin import credentials, firestore
from librouteros import connect
from datetime import datetime
import time

# ——— Initialize Firebase Admin with Firestore ———
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)
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
            print("[*] Found active hotspot users.")
            mac_addresses = [user['mac-address'] for user in active_users]
        else:
            print("[*] No active users. Trying hotspot hosts...")
            hosts = list(api.path('ip', 'hotspot', 'host'))
            mac_addresses = [user['mac-address'] for user in hosts]

        if not mac_addresses:
            print("[!] No MAC addresses found.")
        else:
            for mac in mac_addresses:
                if mac not in known_macs:
                    doc_ref = db.collection('Users Collection').document(mac)  # Use MAC as document ID
                    doc_ref.set({
                        'UserID': mac,
                        'macAddress': mac,
                        'WiFiTimeAvailable': 0,
                        'TotalBottlesDeposited': 0,
                        'SessionStartTime': datetime.now().isoformat(),
                        'SessionEndTime': None
                    })
                    known_macs.add(mac)
                    print(f"[+] Added MAC: {mac} to Firestore under UID: {mac}")
                else:
                    print(f"[-] MAC {mac} already exists in Firestore.")

    except Exception as e:
        print(f"[!] Error while retrieving users: {e}")

    time.sleep(5)  # Wait 5 seconds before checking again
