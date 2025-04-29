import firebase_admin
from firebase_admin import credentials, firestore
from librouteros import connect
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

# ——— Track all devices you already know ———
known_devices = {}  # mac_address: active/inactive

# ——— Continuous Monitoring Loop ———
while True:
    try:
        # Step 1: Get the list of connected devices (Wireless Registration)
        connected_now = set()
        registrations = list(api.path('interface', 'wireless', 'registration-table'))

        for device in registrations:
            mac = device.get('mac-address', '')
            if mac:
                connected_now.add(mac)

        # Step 2: Check each known device
        for mac in known_devices.keys():
            if mac in connected_now and known_devices[mac] != 'active':
                # MAC is connected now, update to active
                doc_ref = db.collection('Users Collection').document(mac)
                doc_ref.update({'status': 'active'})
                known_devices[mac] = 'active'
                print(f"[+] {mac} is now ACTIVE")
            elif mac not in connected_now and known_devices[mac] != 'inactive':
                # MAC is not connected, update to inactive
                doc_ref = db.collection('Users Collection').document(mac)
                doc_ref.update({'status': 'inactive'})
                known_devices[mac] = 'inactive'
                print(f"[-] {mac} is now INACTIVE")

    except Exception as e:
        print(f"[!] Error while monitoring devices: {e}")

    time.sleep(5)  # Wait 5 seconds before checking again
