from librouteros import connect
from librouteros.exceptions import TrapError

# Replace with your MikroTik router's IP and credentials
router_ip = '192.168.88.1'  # or your MikroTik IP
username = 'admin'
password = 'your_password'  # update this

try:
    api = connect(username=username, password=password, host=router_ip, port=8728)

    # Get active hotspot users
    active_users = api.path('ip', 'hotspot', 'active')
    for user in active_users:
        print(f"User: {user.get('user')}, MAC: {user.get('mac-address')}, IP: {user.get('address')}")

except TrapError as e:
    print("API Error:", e)
except Exception as e:
    print("Connection Error:", e)