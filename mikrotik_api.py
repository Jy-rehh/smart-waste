from routeros_api import RouterOsApiPool

def connect_to_mikrotik():
    api_pool = RouterOsApiPool(
    host='192.168.8.104',
    username='apiuser',
    password='apiuser1234',
    port=8728,
    use_ssl=False,
    plaintext_login=True   # <-- Add this line!
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


def disconnect_hotspot_user(username: str):
    api_pool = connect_to_mikrotik()
    api = api_pool.get_api()
    users = api.get_resource('/ip/hotspot/user')
    users.remove(name=username)
    api_pool.disconnect()
    print(f"[MikroTik] Disconnected {username}")
