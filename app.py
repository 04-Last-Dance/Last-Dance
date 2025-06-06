from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from routes.auth import auth_bp
from routes.diary_routes import diary_bp
from routes.music_routes import music_bp
from routes.public import public_bp
from routes.profile import profile_bp
from config.firebase_config import db  # Firebase 설정 임포트

from spotipy.oauth2 import SpotifyOAuth
from config.settings import configure_app

# .env 파일 로드
load_dotenv()
print(f"SPOTIFY_CLIENT_ID from app: {os.getenv('SPOTIFY_CLIENT_ID')}")
print(f"SPOTIFY_CLIENT_SECRET from app: {os.getenv('SPOTIFY_CLIENT_SECRET')}")
print(f"SPOTIFY_REDIRECT_URI from app: {os.getenv('SPOTIFY_REDIRECT_URI')}")

app = Flask(__name__)
CORS(app)
configure_app(app)  # settings.py의 설정 적용


# Firestore 클라이언트를 앱 설정에 저장
app.config['db'] = db

# 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(diary_bp, url_prefix='/api/diary')
app.register_blueprint(music_bp, url_prefix='/api/music')
app.register_blueprint(public_bp)
app.register_blueprint(profile_bp)

# Firebase 설정 반환 엔드포인트
@app.route('/api/firebase-config')
def get_firebase_config():
    """프론트엔드에서 Firebase 설정을 가져올 수 있는 엔드포인트"""
    config = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID')
    }
    return jsonify(config)

# Spotify OAuth 설정
sp_oauth = SpotifyOAuth(
    client_id=app.config['SPOTIFY_CLIENT_ID'],
    client_secret=app.config['SPOTIFY_CLIENT_SECRET'],
    redirect_uri=app.config['SPOTIFY_REDIRECT_URI'],
    scope='user-read-private user-read-currently-playing user-read-recently-played'
)

@app.route('/callback')
def spotify_callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    return redirect('/')  # 성공 후 리디렉트할 페이지

if __name__ == '__main__':
    print("\nLast Dance 서버 시작중...")
    
    auth_url = sp_oauth.get_authorize_url()
    print("\n✅ Spotify 인증 URL (브라우저에서 열기):")
    print(auth_url)
    print(f"\n🚀 서버 실행 중: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)