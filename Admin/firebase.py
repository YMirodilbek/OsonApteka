import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("Admin/firebase.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
