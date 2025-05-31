from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from transformers import pipeline

# Firebase 초기화 (중복 방지)
if not firebase_admin._apps:
    cred = credentials.Certificate('BE/firebase-key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 감정 분석 파이프라인 (Huggingface)
emotion_analyzer = pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base")

diary_bp = Blueprint('diary', __name__)

@diary_bp.route('/submit', methods=['POST'])
def submit_diary():
    data = request.json
    user_id = data.get('user_id')
    text = data.get('text')

    # 감정 분석 실행
    result = emotion_analyzer(text)
    main_emotion = result[0]['label']
    score = result[0]['score']

    # Firestore에 저장
    db.collection('diaries').add({
        'user_id': user_id,
        'text': text,
        'main_emotion': main_emotion,
        'score': score
    })

    return jsonify({
        'message': '일기 제출 및 분석 성공!',
        'main_emotion': main_emotion,
        'score': score
    })
