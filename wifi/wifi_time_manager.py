import time
from librouteros import connect
import firebase_admin
from firebase_admin import credentials, db as realtime_db
import datetime
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

def add_wifi_time(mac_sanitized, added_seconds):
    user_ref = realtime_db.reference(f'users/{mac_sanitized}')
    user_data = user_ref.get()

    now = datetime.datetime.utcnow()
    current_end_time = now

    if user_data and 'WiFiEndTime' in user_data:
        try:
            current_end_time = datetime.datetime.fromisoformat(user_data['WiFiEndTime'])
            if current_end_time < now:
                current_end_time = now
        except ValueError:
            current_end_time = now

    new_end_time = current_end_time + datetime.timedelta(seconds=added_seconds)
    remaining = int((new_end_time - now).total_seconds())

    user_ref.update({
        'WiFiEndTime': new_end_time.isoformat(),
        'WiFiTimeAvailable': remaining
    })

# ---------------- Countdown Loop ----------------
def manage_wifi_time():
    while True:
        try:
            users_ref = realtime_db.reference('users')
            all_users = users_ref.get()

            if not all_users:
                time.sleep(1)
                continue

            now = datetime.datetime.utcnow()

            for mac_sanitized, user_data in all_users.items():
                mac = user_data.get('UserID', '').upper()
                end_time_str = user_data.get('WiFiEndTime', '')
                done_clicked = user_data.get('DoneClicked', False)

                if not mac or not end_time_str:
                    continue

                try:
                    end_time = datetime.datetime.fromisoformat(end_time_str)
                except ValueError:
                    continue  # Skip users with invalid time format

                # Compare current time to end time
                if now < end_time:
                    remaining_seconds = int((end_time - now).total_seconds())
                    users_ref.child(mac_sanitized).update({
                        'WiFiTimeAvailable': remaining_seconds
                    })
                    add_or_update_binding(mac, 'bypassed')
                else:
                    users_ref.child(mac_sanitized).update({
                        'WiFiTimeAvailable': 0
                    })
                    add_or_update_binding(mac, 'regular')

            time.sleep(1)

        except Exception as e:
            time.sleep(1)

        except Exception as e:
            time.sleep(1)

if __name__ == "__main__":
    manage_wifi_time()
