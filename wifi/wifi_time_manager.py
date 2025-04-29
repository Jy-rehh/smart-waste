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
    current_binding = None

    while True:
        try:
            users_ref = db.collection('Users Collection')
            users = users_ref.where('macAddress', '!=', '').stream()

            for user in users:
                user_data = user.to_dict()
                mac = user_data.get('macAddress', '').upper()
                time_left = user_data.get('WiFiTimeAvailable', 0)

                if mac and time_left > 0:
                    new_time = time_left - 1
                    users_ref.document(user.id).update({'WiFiTimeAvailable': new_time})
                    print(f"[↓] {mac} - WiFiTimeAvailable: {new_time}")

                    if current_binding != 'bypassed':
                        add_or_update_binding(mac, 'bypassed')
                        current_binding = 'bypassed'
                else:
                    if mac and current_binding != 'regular':
                        add_or_update_binding(mac, 'regular')
                        current_binding = 'regular'

        except Exception as e:
            print(f"[!] Error managing time: {e}")

        time.sleep(1)

if __name__ == "__main__":
    manage_time()
