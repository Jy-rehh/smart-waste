import time
from librouteros import connect

# Settings
ROUTER_HOST = '192.168.50.1'
ROUTER_USERNAME = 'admin'
ROUTER_PASSWORD = ''
TARGET_MAC = 'A2:DE:BF:8C:50:87'  # <<< Your device MAC

# Connect to MikroTik Router
try:
    api = connect(username=ROUTER_USERNAME, password=ROUTER_PASSWORD, host=ROUTER_HOST)
    print("[*] Connected to MikroTik Router.")
except Exception as e:
    print(f"[!] Connection failed: {e}")
    exit()

# MikroTik IP Binding path
bindings = api.path('ip', 'hotspot', 'ip-binding')

def find_binding(mac_address):
    try:
        # Use 'print' command to get list of bindings
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
            # Update the existing entry (make sure the correct keys are passed)
            bindings.update(
                **{
                    '.id': existing['.id'],
                    'type': binding_type
                }
            )
            print(f"[*] Updated MAC {mac_address} to '{binding_type}'.")
        else:
            # Add a new binding if none exists (adjust parameter names)
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

# Initial setup: Make sure MAC exists
add_or_update_binding(TARGET_MAC, 'bypassed')

# Now toggle every 10 seconds
current_type = 'bypassed'

try:
    while True:
        # Switch type
        new_type = 'regular' if current_type == 'bypassed' else 'bypassed'
        add_or_update_binding(TARGET_MAC, new_type)
        current_type = new_type

        time.sleep(10)  # Wait for 10 seconds before the next toggle
except KeyboardInterrupt:
    print("\n[*] Script stopped by user.")
except Exception as e:
    print(f"[!] Unexpected error: {e}")
