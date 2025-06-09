from flask import Blueprint, render_template, session, redirect, url_for, make_response
from services.auth import auth_required
from firebase_admin import firestore
from datetime import datetime, date

public_bp = Blueprint('public', __name__)
db = firestore.client()

@public_bp.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('public.dashboard'))
    return render_template('home.html')

@public_bp.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('public.dashboard'))
    return render_template('login.html')

@public_bp.route('/signup')
def signup():
    if 'user' in session:
        return redirect(url_for('public.dashboard'))
    return render_template('signup.html')

@public_bp.route('/logout')
def logout():
    session.pop('user', None)
    response = make_response(redirect(url_for('public.home')))
    response.set_cookie('session', '', expires=0)
    return response

@public_bp.route('/dashboard')
@auth_required
def dashboard():
    return render_template('dashboard.html')

@public_bp.route('/write-diary')
def write_diary():
    return render_template('write_diary.html')

@public_bp.route("/calendar")
def emotion_calendar():
    # Firestore에서 최근 100개의 일기 불러오기
    docs = db.collection("diaries") \
        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
        .limit(100) \
        .stream()

    # 날짜별로 마지막 일기만 저장
    date_to_emotion = {}
    for doc in docs:
        data = doc.to_dict()
        ts = data.get("timestamp")
        emotion = data.get("main_emotion")

        if ts and emotion:
            date_key = ts.date()
            if date_key not in date_to_emotion:
                date_to_emotion[date_key] = emotion

    # 현재 달 기준 달력 생성
    today = date.today()
    year = today.year
    month = today.month

    first_day = date(year, month, 1)
    first_weekday = first_day.weekday()

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    num_days = (next_month - first_day).days

    calendar = []
    for i in range(first_weekday):
        calendar.append({ "date": None, "emotion": None, "is_today": False })

    for day in range(1, num_days + 1):
        d = date(year, month, day)
        calendar.append({
            "date": d,
            "emotion": date_to_emotion.get(d),
            "is_today": (d == today)
        })

    return render_template("calendar.html", calendar=calendar)
