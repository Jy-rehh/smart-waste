from flask import Flask, request, jsonify
from librouteros import connect

app = Flask(__name__)

def get_mac_from_ip(client_ip):
    try:
        # Connect to MikroTik Router
        api = connect(username='admin', password='', host='192.168.50.1')  # Replace with your credentials
        leases = api('/ip/dhcp-server/lease/print')
        
        # Look for matching IP address in leases
        for lease in leases:
            if lease.get('address') == client_ip:
                return lease.get('mac-address')
        return None
    except Exception as e:
        return str(e)

@app.route('/get-mac', methods=['GET'])
def get_mac():
    client_ip = request.args.get('ip')  # Get IP address from query params
    mac_address = get_mac_from_ip(client_ip)
    
    if mac_address:
        return jsonify({'mac-address': mac_address})
    else:
        return jsonify({'error': 'MAC address not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
