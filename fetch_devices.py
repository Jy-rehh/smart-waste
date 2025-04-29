# fetch_devices.py
import librouteros
import json

def fetch_devices():
    try:
        # Connect to MikroTik RouterOS
        api = librouteros.connect(
            host='192.168.50.1',  # MikroTik IP
            username='admin',      # Replace with your username
            password='',           # Replace with your password
            plaintext_login=True
        )

        # Fetch ARP list from RouterOS
        arp_list = api('/ip/arp/print')

        devices = []
        for entry in arp_list:
            devices.append({
                'ipAddress': entry.get('address'),
                'macAddress': entry.get('mac-address')
            })

        return devices
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    devices = fetch_devices()
    print(json.dumps(devices))  # Output the result as JSON
