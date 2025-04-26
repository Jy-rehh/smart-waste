import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
users_ref = db.collection('users')

# Function to update time based on bottle inserted
def update_user_time(user_id, additional_time):
    user_doc = users_ref.document(user_id)
    user_data = user_doc.get().to_dict()
    if user_data:
        new_time_remaining = user_data['time_remaining'] + additional_time
        user_doc.update({'time_remaining': new_time_remaining})
        print(f"User {user_id} now has {new_time_remaining} minutes left.")
