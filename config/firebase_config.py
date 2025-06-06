import firebase_admin
from firebase_admin import credentials, firestore
import os

def initialize_firebase():
    """Firebase를 초기화하고 필요한 클라이언트를 반환합니다."""
    try:
        # 이미 초기화되어 있는지 확인
        firebase_admin.get_app()
        print("✅ Firebase가 이미 초기화되어 있습니다.")
    except ValueError:
        # 초기화되지 않은 경우에만 초기화
        cred = credentials.Certificate("firebase-auth.json")
        firebase_admin.initialize_app(cred)
        print("✅ Firebase 초기화 완료")

    # Firestore 클라이언트 반환
    return firestore.client()

# Firebase 초기화 및 Firestore 클라이언트 생성
db = initialize_firebase() 