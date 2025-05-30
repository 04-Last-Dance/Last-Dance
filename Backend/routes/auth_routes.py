from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화 (중복 방지)
if not firebase_admin._apps:
    cred = credentials.Certificate('BE/firebase-key.json')
    firebase_admin.initialize_app(cred)

# firebase-admin에서 제공하는 firestore client 사용
db = firestore.client()

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user_id = data.get('id')
    password = data.get('password')
    email = data.get('email')

    # 기존 사용자 확인
    user_ref = db.collection('users').document(user_id)
    if user_ref.get().exists:
        return jsonify({'message': '이미 존재하는 사용자 ID입니다.'}), 400

    # 새 사용자 추가
    user_ref.set({
        'password': password,
        'email': email
    })
    return jsonify({'message': '회원가입 성공!'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('id')
    password = data.get('password')

    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({'message': '존재하지 않는 사용자입니다.'}), 404

    user_data = user_doc.to_dict()
    if user_data['password'] != password:
        return jsonify({'message': '비밀번호가 일치하지 않습니다.'}), 401

    return jsonify({'message': '로그인 성공!'})
