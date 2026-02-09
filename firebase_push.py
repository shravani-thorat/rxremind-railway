import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv
import sqlite3
import os
import json

load_dotenv()

service_account_info = json.loads(os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON"))

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pharmacy.db")

def send_push(title, body):
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT token FROM fcm_tokens")
    tokens = [row[0] for row in cursor.fetchall()]
    conn.close()

    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )

        messaging.send(message)