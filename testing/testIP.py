# server.py
from flask import Flask, request, jsonify
from librouteros import connect

app = Flask(__name__)

def get_mac_from_ip(client_ip):
    api = connect(username='admin', password='', host='192.168.50.1')  # <-- Change password here!

    leases = api('/ip/dhcp-server/lease/print')
    for lease in leases:
        if lease.get('address') == client_ip:
            return lease.get('mac-address')
    return None

@app.route('/')
def home():
    client_ip = request.remote_addr  # Get the IP of the connected device
    mac_address = get_mac_from_ip(client_ip)

    if mac_address:
        return f'''
            <h1>Connected Device Info</h1>
            <p><strong>IP Address:</strong> {client_ip}</p>
            <p><strong>MAC Address:</strong> {mac_address}</p>
        '''
    else:
        return f'''
            <h1>Device Info Not Found</h1>
            <p><strong>IP Address:</strong> {client_ip}</p>
            <p><strong>MAC Address:</strong> Not found in DHCP leases.</p>
        '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
