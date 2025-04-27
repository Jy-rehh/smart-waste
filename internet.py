from librouteros import connect

# Connect to MikroTik Router
try:
    api = connect(username='admin', password='', host='192.168.50.1')
    print("[*] Connected to MikroTik Router.")
except Exception as e:
    print(f"[!] Connection failed: {e}")
    exit()

# Hardcode a test MAC address
test_mac = "A2:DE:BF:8C:50:87"  # <<< change this to your device's real MAC address

try:
    # Correct parameter names
    api.path('ip', 'hotspot', 'ip-binding').add(
        **{
            'mac-address': test_mac,
            'type': 'bypassed',
            'comment': 'Connected'
        }
    )
    print(f"[*] Successfully bypassed MAC: {test_mac}")
except Exception as e:
    print(f"[!] Failed to bypass MAC: {e}")
