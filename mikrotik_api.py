from routeros_api import RouterOsApiPool

def connect_to_mikrotik():
    api_pool = RouterOsApiPool(
        host='192.168.50.1',  # replace with your MikroTik's IP
        username='apiuser',   # replace with your MikroTik API user
        password='yourpassword',  # replace with that user's password
        port=8728,
        use_ssl=False
    )
    return api_pool

def create_hotspot_user(username, password='userpass', time_minutes=15):
    api_pool = connect_to_mikrotik()
    api = api_pool.get_api()

    hotspot_user = api.get_resource('/ip/hotspot/user')

    # Optional: sanitize username
    username = username.replace('@', '').replace('.', '')

    hotspot_user.add(
        name=username,
        password=password,
        limit_uptime=f'00:{time_minutes:02}:00',
        profile='default'
    )

    print(f"User {username} created with {time_minutes} minutes of access.")
    api_pool.disconnect()