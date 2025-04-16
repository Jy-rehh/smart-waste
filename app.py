import firebase_admin
from firebase_admin import credentials, firestore

# Path to your JSON key
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

# Example: Add data
doc_ref = db.collection("bins").document("bin1")
doc_ref.set({
    "status": "empty",
    "last_updated": firestore.SERVER_TIMESTAMP
})

print("Data sent to Firestore!")
