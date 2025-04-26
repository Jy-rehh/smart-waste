from flask import Flask, request, render_template
from librouteros import connect

app = Flask(__name__)

# Function to get MAC address from IP
def get_mac_from_ip(client_ip):
    try:
        api = connect(username='admin', password='1234', host='192.168.50.1')
        hosts = api(cmd='/ip/hotspot/host/print')
        
        for host in hosts:
            if host.get('address') == client_ip:
                return host.get('mac-address')  # Return the MAC address
    except Exception as e:
        print("Error:", e)
    return None

# Function to grant internet access based on MAC address
def grant_internet(mac_address, duration):
    try:
        api = connect(username='admin', password='1234', host='192.168.50.1')
        users = api(cmd='/ip/hotspot/user/print')
        
        user_exists = False
        for user in users:
            if user.get('name') == mac_address:
                user_exists = True
                user_id = user['.id']
                break

        if user_exists:
            # Update the existing user with the new limit (time)
            api(cmd='/ip/hotspot/user/set', **{
                '.id': user_id,
                'limit-uptime': duration
            })
            print(f"Updated time for {mac_address}")
        else:
            # Create a new user for the device
            api(cmd='/ip/hotspot/user/add', **{
                'name': mac_address,
                'password': '',
                'limit-uptime': duration,
                'profile': 'default'
            })
            print(f"Added new user {mac_address}")
    except Exception as e:
        print("Error granting internet:", e)

# Route for handling the login and granting access
@app.route("/grant-access", methods=["POST"])
def grant_access():
    client_ip = request.remote_addr  # Get the IP address of the connected client
    mac = get_mac_from_ip(client_ip)

    if mac:
        print(f"MAC Address: {mac}")
        grant_internet(mac, "30m")  # Give 30 minutes of internet access
        return "Access granted for 30 minutes."
    else:
        return "Failed to get MAC address."

# Route for showing login page (you probably have this already)
@app.route("/")
def home():
    return render_template("/templates/login.html")  # Your custom login page

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
