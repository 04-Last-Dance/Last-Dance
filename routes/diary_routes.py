from flask import Blueprint, request, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore, auth
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

def get_current_user_uid():
    """현재 로그인한 사용자의 UID 가져오기"""
    # Option 1: 프론트엔드에서 전송된 ID Token 검증
    id_token = request.headers.get('Authorization')
    if id_token and id_token.startswith('Bearer '):
        try:
            decoded_token = auth.verify_id_token(id_token.split('Bearer ')[1])
            return decoded_token['uid']
        except:
            return None
    
    # Option 2: 세션에서 가져오기 (세션 방식 사용 시)
    return session.get('user_uid')

def _get_user_diaries_collection(user_uid: str):
    """사용자별 다이어리 컬렉션 참조 반환 - diary1/{user_uid}/diaries/"""
    return db.collection('diary1').document(user_uid).collection('diaries')

def _get_all_diaries():
    """모든 사용자의 다이어리를 가져오는 헬퍼 함수"""
    all_diaries = []
    
    # 기존 구조에서 가져오기 (diaries/{diary_id})
    old_docs = db.collection('diaries').stream()
    for doc in old_docs:
        data = doc.to_dict()
        if data and 'content' in data:  # 실제 다이어리 데이터인지 확인
            all_diaries.append(data)
    
    # 새 구조에서 가져오기 (diaries/{user_id}/diaries/{diary_id})
    users_collection = db.collection('diaries').stream()
    for user_doc in users_collection:
        user_id = user_doc.id
        user_diaries = _get_user_diaries_collection(user_id).stream()
        for diary_doc in user_diaries:
            data = diary_doc.to_dict()
            if data:
                all_diaries.append(data)
    
    return all_diaries

@diary_bp.route('/submit', methods=['POST'])
def submit_diary():
    # 세션에서 사용자 정보 가져오기
    user = session.get('user', {})
    user_uid = user.get('uid')
    
    if not user_uid:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    data = request.get_json()
    content = data.get('content')
    emotions = data.get('emotions', [])

    if not content or not emotions:
        return jsonify({'error': '내용과 감정을 모두 입력해주세요.'}), 400

    # 감정 분석
    result = emotion_analyzer(content)
    main_emotion = result[0]['label']
    score = result[0]['score']

    # diary1/{user_uid}/diaries/{diary_id} 구조로 저장
    _get_user_diaries_collection(user_uid).add({
        'content': content,
        'user_emotions': emotions,
        'main_emotion': main_emotion,
        'score': score,
        'user_id': user_uid,
        'timestamp': datetime.utcnow()
    })

    return jsonify({
        'message': '일기 저장 및 분석 성공',
        'main_emotion': emotion_translation.get(main_emotion, main_emotion),
        'score': score
    })

@diary_bp.route('/recent', methods=['GET'])
def get_recent_diaries():
    user_uid = get_current_user_uid()
    if not user_uid:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    # 해당 사용자의 최근 다이어리 3개 가져오기
    diaries = _get_user_diaries_collection(user_uid) \
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
    user_uid = get_current_user_uid()
    if not user_uid:
        return jsonify({'main_emotion': 'neutral', 'score': 0})
    
    diaries = _get_user_diaries_collection(user_uid) \
        .order_by('timestamp', direction=firestore.Query.DESCENDING) \
        .limit(1).stream()
    
    for d in diaries:
        doc = d.to_dict()
        return jsonify({
            'main_emotion': doc.get('main_emotion', 'neutral'),
            'score': doc.get('score', 0)
        })

    return jsonify({'main_emotion': 'neutral', 'score': 0})

@diary_bp.route("/by-date")
def diary_by_date():
    date_str = request.args.get("date")
    user_id = request.args.get('user_id', 'default_user')  # user_id 파라미터 추가
    
    if not date_str:
        return jsonify({"error": "날짜가 필요합니다"}), 400

    start = datetime.strptime(date_str, "%Y-%m-%d")
    end = start + timedelta(days=1)

    query = _get_user_diaries_collection(user_id) \
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
    user_id = request.args.get('user_id', 'default_user')  # user_id 파라미터 추가
    
    from datetime import datetime
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    docs = _get_user_diaries_collection(user_id) \
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
    # 세션에서 사용자 정보 가져오기
    user = session.get('user', {})
    user_uid = user.get('uid')
    
    if not user_uid:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    try:
        # diary1/{user_uid}/diaries 에서 일기 가져오기
        diaries_ref = _get_user_diaries_collection(user_uid)
        diaries = diaries_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()

        result = []
        emotion_map = {
            "joy": "😄 기쁨", "sadness": "😢 슬픔", "anger": "😡 분노", 
            "fear": "😨 두려움", "disgust": "🤢 혐오", 
            "surprise": "😲 놀람", "neutral": "😐 중립"
        }

        for diary in diaries:
            doc = diary.to_dict()
            timestamp = doc.get('timestamp')
            if isinstance(timestamp, datetime):
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
            else:
                formatted_time = "날짜 없음"

            result.append({
                "content": doc.get("content", "")[:100],
                "emotion": emotion_map.get(doc.get("main_emotion", "neutral"), "😐 중립"),
                "score": round(doc.get("score", 0), 2),
                "timestamp": formatted_time
            })

        return render_template("all_diaries.html", diaries=result)
        
    except Exception as e:
        print(f"Error loading diaries: {str(e)}")
        return render_template("all_diaries.html", diaries=[])
    
@diary_bp.route('/weekly-emotions', methods=['GET'])
def weekly_emotions():
    user_id = request.args.get('user_id', 'default_user')  # user_id 파라미터 추가
    
    from datetime import datetime, timedelta

    today = datetime.utcnow()
    start = today - timedelta(days=today.weekday())  # 이번 주 월요일
    end = start + timedelta(days=7)

    result = {}  # {"Mon": "joy", ...}

    for i in range(7):
        day = start + timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)

        docs = _get_user_diaries_collection(user_id) \
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