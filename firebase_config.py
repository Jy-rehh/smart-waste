import firebase_admin
from firebase_admin import credentials, db

# Path to your Firebase config JSON
cred = credentials.Certificate("templates/firebase_config.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-waste-smart-access-a425c-default-rtdb.firebaseio.com/'
})

ref = db.reference('/test_data')  # Reference to where data will be saved
ref.set({
    'status': 'working',
    'message': 'Firebase connected!'
})

print("Data pushed to Firebase.")
