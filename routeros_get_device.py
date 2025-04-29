# routeros_get_device.py
from librouteros import connect
import sys
import json

def get_device_info(mac_address):
    # Connect to MikroTik RouterOS
    api = connect(username='admin', password='', host='192.168.50.1')

    # Fetch the wireless registration table
    result = api('/interface/wireless/registration-table/print')

    # Iterate through the devices and find the one matching the MAC address
    for device in result:
        if device.get('mac-address') == mac_address:
            return {
                'ipAddress': device.get('ip-address'),
                'macAddress': device.get('mac-address')
            }

    # If device is not found, return None
    return None

if __name__ == '__main__':
    # Get MAC address from command-line argument
    mac_address = sys.argv[1]
    
    # Get device info
    device_info = get_device_info(mac_address)
    
    if device_info:
        print(json.dumps(device_info))  # Output JSON data
    else:
        print(json.dumps({'error': 'Device not found'}))
