import time
from datetime import datetime
from librouteros import connect
import firebase_admin
from firebase_admin import credentials, db as realtime_db

# ---------------- Firebase Realtime DB ----------------
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-waste-c39ac-default-rtdb.firebaseio.com/'
})

# ---------------- MikroTik Router ----------------
ROUTER_HOST = '192.168.50.1'
ROUTER_USERNAME = 'admin'
ROUTER_PASSWORD = ''

try:
    api = connect(username=ROUTER_USERNAME, password=ROUTER_PASSWORD, host=ROUTER_HOST)
    # print("[*] Connected to MikroTik Router.")
except Exception as e:
    # print(f"[!] MikroTik connection failed: {e}")
    exit()

bindings = api.path('ip', 'hotspot', 'ip-binding')

def find_binding(mac_address):
    try:
        for entry in bindings('print'):
            if entry.get('mac-address', '').upper() == mac_address.upper():
                return entry
    except Exception as e:
        pass  # Optional: log to file if needed
    return None

def add_or_update_binding(mac_address, binding_type):
    try:
        existing = find_binding(mac_address)
        if existing:
            bindings.update(**{
                '.id': existing['.id'],
                'type': binding_type
            })
        else:
            bindings.add(**{
                'mac-address': mac_address,
                'type': binding_type,
                'comment': 'Connected'
            })
    except Exception as e:
        pass  # Optional: log to file if needed

# ---------------- Countdown Loop ----------------
def manage_wifi_time():
    while True:
        try:
            users_ref = realtime_db.reference('users')
            all_users = users_ref.get()

            if not all_users:
                time.sleep(1)
                continue

            current_time = int(time.time())

            for mac_sanitized, user_data in all_users.items():
                mac = user_data.get('UserID', '').upper()
                time_left = user_data.get('WiFiTimeAvailable', 0)
                end_time = user_data.get('WiFiEndTime', 0)
                
                if not mac:
                    continue

                # Migrate old WiFiTimeAvailable to WiFiEndTime (if needed)
                if time_left > 0 and end_time == 0:
                    new_end_time = current_time + time_left
                    users_ref.child(mac_sanitized).update({
                        'WiFiEndTime': new_end_time,
                        'WiFiTimeAvailable': None  # Delete old field
                    })
                    end_time = new_end_time  # Use the new value

                # Check if WiFi time has expired
                if end_time > 0:
                    if current_time >= end_time:
                        # Delete WiFiEndTime and set to regular access
                        users_ref.child(mac_sanitized).update({
                            'WiFiEndTime': None  # Deletes the field
                        })
                        add_or_update_binding(mac, 'regular')
                    else:
                        add_or_update_binding(mac, 'bypassed')

            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    manage_wifi_time()
