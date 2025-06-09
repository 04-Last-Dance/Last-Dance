import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import current_app
from config.firebase_config import db

# Firebase 앱이 이미 초기화되어 있는지 확인
try:
    firebase_admin.get_app()
except ValueError:
    print("❌ Firebase가 초기화되지 않았습니다. config/firebase_config.py를 먼저 임포트하세요.")
    raise

def verify_token(token):
    """Firebase ID 토큰을 검증합니다."""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        current_app.logger.error(f"Token verification failed: {str(e)}")
        return None
