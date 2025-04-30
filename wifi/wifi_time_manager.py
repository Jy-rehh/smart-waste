import time
from librouteros import connect
import firebase_admin
from firebase_admin import credentials, db as realtime_db

# ---------------- Firebase Realtime DB ----------------
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-waste-c39ac-default-rtdb.firebaseio.com/'  # <-- Replace with your actual database URL
})

# ---------------- MikroTik Router ----------------
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
def manage_wifi_time():
    try:
        users_ref = realtime_db.reference('users')
        all_users = users_ref.get()

        if not all_users:
            print("[!] No users found in Realtime DB.")
            return

        for mac_sanitized, user_data in all_users.items():
            mac = user_data.get('UserID', '').upper()
            time_left = user_data.get('WiFiTimeAvailable', 0)

            if mac:
                if time_left > 0:
                    # If time left, set to 'bypassed'
                    add_or_update_binding(mac, 'bypassed')
                    print(f"[↓] {mac} - WiFiTimeAvailable: {time_left} (bypassed)")
                else:
                    # If no time left, set to 'regular'
                    add_or_update_binding(mac, 'regular')
                    print(f"[↑] {mac} - WiFiTimeAvailable is 0 (regular)")

    except Exception as e:
        print(f"[!] Error managing WiFi time: {e}")

        time.sleep(1)

if __name__ == "__main__":
    manage_wifi_time()
