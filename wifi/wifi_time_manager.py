# wifi_time_manager.py

import time
from librouteros import connect
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------- Firebase ----------------
cred = credentials.Certificate('firebase-key.json')  # <-- Put your JSON path
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------- MikroTik ----------------
ROUTER_HOST = '192.168.50.1'
ROUTER_USERNAME = 'admin'
ROUTER_PASSWORD = ''

try:
    api = connect(username=ROUTER_USERNAME, password=ROUTER_PASSWORD, host=ROUTER_HOST)
    print("[*] Connected to MikroTik Router.")
except Exception as e:
    print(f"[!] MikroTik connection failed: {e}")
    exit()

bindings = api.path('ip', 'hotspot', 'ip-binding')

def find_binding(mac_address):
    try:
        for entry in bindings('print'):
            if entry.get('mac-address', '').upper() == mac_address.upper():
                return entry
    except Exception as e:
        print(f"[!] Error fetching bindings: {e}")
    return None

def add_or_update_binding(mac_address, binding_type):
    try:
        existing = find_binding(mac_address)
        if existing:
            bindings.update(
                **{
                    '.id': existing['.id'],
                    'type': binding_type
                }
            )
            print(f"[*] Updated MAC {mac_address} to '{binding_type}'.")
        else:
            bindings.add(
                **{
                    'mac-address': mac_address,
                    'type': binding_type,
                    'comment': 'Connected'
                }
            )
            print(f"[*] Added new MAC {mac_address} with type '{binding_type}'.")
    except Exception as e:
        print(f"[!] Error adding/updating binding: {e}")

# ---------------- Countdown Loop ----------------
def manage_time():
    while True:
        try:
            users_ref = db.collection('Users Collection')
            users = users_ref.where('macAddress', '!=', '').stream()

            for user in users:
                user_data = user.to_dict()
                mac = user_data.get('macAddress', '').upper()
                time_left = user_data.get('WiFiTimeAvailable', 0)

                if mac:
                    if time_left > 0:
                        # Update the WiFi time for this user
                        new_time = time_left - 1
                        users_ref.document(user.id).update({'WiFiTimeAvailable': new_time})
                        print(f"[↓] {mac} - WiFiTimeAvailable: {new_time}")

                        # Set the binding to 'bypassed' if it's not already
                        add_or_update_binding(mac, 'bypassed')
                    else:
                        # If time is 0, change to 'regular' status
                        add_or_update_binding(mac, 'regular')
                        print(f"[↑] {mac} - WiFiTimeAvailable is 0, set to 'regular' status.")

        except Exception as e:
            print(f"[!] Error managing time: {e}")

        time.sleep(1)