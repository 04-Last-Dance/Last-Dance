import firebase_admin
from firebase_admin import credentials, firestore
import os

# 현재 파일 위치 기준으로 절대경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(current_dir, 'firebase-key.json')

cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

# 테스트: users 컬렉션에 데이터 추가
def test_add_user():
    doc_ref = db.collection('users').document('testuser')
    doc_ref.set({
        'name': 'Test User',
        'email': 'test@example.com'
    })
    print("✅ Firebase에 testuser 추가 완료")

if __name__ == '__main__':
    test_add_user()
