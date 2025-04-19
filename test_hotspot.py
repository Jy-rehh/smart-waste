from mikrotik_api import create_hotspot_user

# Try creating a MikroTik hotspot user with 15 minutes access
create_hotspot_user(username="test_user", time_minutes=15)