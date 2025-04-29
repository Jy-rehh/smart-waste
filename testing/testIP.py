from flask import Flask, render_template_string
import subprocess
import os

app = Flask(__name__)

def ping_all_devices():
    base_ip = "192.168.1."
    for i in range(2, 255):
        os.system(f"ping -c 1 -W 1 {base_ip}{i} > /dev/null")

def get_connected_devices():
    ping_all_devices()
    output = subprocess.check_output("arp -a", shell=True).decode()
    devices = []
    for line in output.splitlines():
        if '(' in line:
            parts = line.split()
            ip = parts[1].strip('()')
            mac = parts[3]
            devices.append({'ip': ip, 'mac': mac})
    return devices

@app.route('/')
def portal():
    devices = get_connected_devices()
    html = '''
    <h1>Welcome to Piso WiFi Portal</h1>
    <table border="1">
        <tr><th>IP Address</th><th>MAC Address</th></tr>
        {% for device in devices %}
        <tr><td>{{ device.ip }}</td><td>{{ device.mac }}</td></tr>
        {% endfor %}
    </table>
    '''
    return render_template_string(html, devices=devices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)  # Or port=5000 first for testing
