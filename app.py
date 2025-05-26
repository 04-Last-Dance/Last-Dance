from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# .env 읽어오기
load_dotenv()

app = Flask(__name__)
configure_app(app)

# Firebase 인증 키 파일 경로
cred = credentials.Certificate("firebase-auth.json")
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 사용
db = firestore.client()

def get_firebase_config():
    config = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID')
    }
    return jsonify(config)

if __name__ == '__main__':
    app.run(debug=True)