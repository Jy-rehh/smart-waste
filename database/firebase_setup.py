import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials (Replace with your actual JSON file)
cred = credentials.Certificate("templates/firebase_config.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Test: Fetch all documents from "Transaction Collection"
transactions_ref = db.collection("Transaction Collection")
docs = transactions_ref.stream()

print("Connected to Firestore! Retrieved Transactions:")
for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")
