from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from transformers import pipeline
from datetime import datetime, timedelta
from flask import render_template

# Firebase 초기화 (중복 방지)
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase-auth.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 감정 분석 파이프라인
emotion_analyzer = pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base")

# 감정 이모지 및 한국어 매핑
emotion_translation = {
    'anger': '😡 분노',
    'disgust': '🤢 혐오',
    'fear': '😨 두려움',
    'joy': '😊 행복',
    'sadness': '😢 슬픔',
    'surprise': '😮 놀람',
    'neutral': '😐 중립'
}

diary_bp = Blueprint('diary', __name__)

@diary_bp.route('/submit', methods=['POST'])
def submit_diary():
    data = request.get_json()
    content = data.get('content')
    emotions = data.get('emotions', [])

    if not content or not emotions:
        return jsonify({'error': '내용과 감정을 모두 입력해주세요.'}), 400

    # 감정 분석
    result = emotion_analyzer(content)
    main_emotion = result[0]['label']
    score = result[0]['score']

    # Firestore에 저장
    db.collection('diaries').add({
        'content': content,
        'user_emotions': emotions,
        'main_emotion': main_emotion,
        'score': score,
        'timestamp': datetime.utcnow()
    })

    return jsonify({
        'message': '일기 저장 및 분석 성공',
        'main_emotion': emotion_translation.get(main_emotion, main_emotion),
        'score': score
    })

@diary_bp.route('/recent', methods=['GET'])
def get_recent_diaries():
    diaries = db.collection('diaries') \
        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
        .limit(3).stream()

    result = []
    for d in diaries:
        doc = d.to_dict()
        result.append({
            'content': doc.get('content'),
            'main_emotion': emotion_translation.get(doc.get('main_emotion', ''), doc.get('main_emotion')),
            'score': doc.get('score'),
            'timestamp': doc.get('timestamp').isoformat() if doc.get('timestamp') else ''
        })
    return jsonify(result)

@diary_bp.route('/last-emotion', methods=['GET'])
def get_last_emotion():
    diaries = db.collection('diaries') \
        .order_by('timestamp', direction=firestore.Query.DESCENDING) \
        .limit(1).stream()
    
    for d in diaries:
        doc = d.to_dict()
        return jsonify({
            'main_emotion': doc.get('main_emotion', 'neutral'),
            'score': doc.get('score', 0)
        })

    return jsonify({'main_emotion': 'neutral', 'score': 0})

@diary_bp.route("/by-date")  # ✅ 여기 수정됨
def diary_by_date():
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "날짜가 필요합니다"}), 400

    start = datetime.strptime(date_str, "%Y-%m-%d")
    end = start + timedelta(days=1)

    query = db.collection("diaries") \
        .where("timestamp", ">=", start) \
        .where("timestamp", "<", end) \
        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
        .limit(1) \
        .stream()

    for doc in query:
        data = doc.to_dict()
        emotion = data.get("main_emotion", "neutral")
        return jsonify({
            "content": data.get("content", "내용 없음"),
            "emotion": emotion,
            "emotion_kr": {
                "joy": "기쁨", "sadness": "슬픔", "anger": "분노", "fear": "두려움",
                "disgust": "혐오", "surprise": "놀람", "neutral": "중립"
            }.get(emotion, "중립"),
            "emotion_emoji": {
                "joy": "😄", "sadness": "😢", "anger": "😡", "fear": "😨",
                "disgust": "🤢", "surprise": "😲", "neutral": "😐"
            }.get(emotion, "😐")
        })

    return jsonify({
        "content": "작성된 일기가 없습니다.",
        "emotion": "neutral", "emotion_kr": "중립", "emotion_emoji": "😐"
    })

@diary_bp.route('/monthly-stats', methods=['GET'])
def monthly_stats():
    from datetime import datetime
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    docs = db.collection("diaries") \
        .where("timestamp", ">=", start_of_month) \
        .stream()

    count = 0
    score_sum = 0
    emotion_counter = {}

    for doc in docs:
        data = doc.to_dict()
        score = data.get("score", 0)
        emotion = data.get("main_emotion", "neutral")

        count += 1
        score_sum += score
        emotion_counter[emotion] = emotion_counter.get(emotion, 0) + 1

    if count > 0:
        average_score = round(score_sum / count, 2)
        most_common_emotion = max(emotion_counter, key=emotion_counter.get)
    else:
        average_score = "-"
        most_common_emotion = "neutral"

    emotion_kr = {
        "joy": "기쁨", "sadness": "슬픔", "anger": "분노", "fear": "두려움",
        "disgust": "혐오", "surprise": "놀람", "neutral": "중립"
    }
    emotion_emoji = {
        "joy": "😄", "sadness": "😢", "anger": "😡", "fear": "😨",
        "disgust": "🤢", "surprise": "😲", "neutral": "😐"
    }

    return jsonify({
        "diary_count": count,
        "average_score": average_score,
        "most_common_emotion": most_common_emotion,
        "most_common_emotion_kr": emotion_kr.get(most_common_emotion, "중립"),
        "most_common_emotion_emoji": emotion_emoji.get(most_common_emotion, "😐")
    })

@diary_bp.route('/all', methods=['GET'])
def view_all_diaries():
    diaries = db.collection('diaries') \
        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
        .stream()

    result = []
    emotion_map = {
        "joy": "😄 기쁨", "sadness": "😢 슬픔", "anger": "😡 분노", "fear": "😨 두려움",
        "disgust": "🤢 혐오", "surprise": "😲 놀람", "neutral": "😐 중립"
    }

    for d in diaries:
        doc = d.to_dict()
        result.append({
            "content": doc.get("content", "")[:100],
            "emotion": emotion_map.get(doc.get("main_emotion", "neutral"), "😐 중립"),
            "score": round(doc.get("score", 0), 2),
            "timestamp": doc.get("timestamp").strftime("%Y-%m-%d %H:%M")
        })

    return render_template("all_diaries.html", diaries=result)

@diary_bp.route('/weekly-emotions', methods=['GET'])
def weekly_emotions():
    from datetime import datetime, timedelta

    today = datetime.utcnow()
    start = today - timedelta(days=today.weekday())  # 이번 주 월요일
    end = start + timedelta(days=7)

    result = {}  # {"2025-06-03": "joy", ...}

    for i in range(7):
        day = start + timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)

        docs = db.collection("diaries") \
            .where("timestamp", ">=", day_start) \
            .where("timestamp", "<", day_end) \
            .order_by("timestamp", direction=firestore.Query.DESCENDING) \
            .limit(1).stream()

        for doc in docs:
            data = doc.to_dict()
            result[day.strftime("%a")] = data.get("main_emotion", "neutral")
            break
        else:
            result[day.strftime("%a")] = None

    return jsonify(result)