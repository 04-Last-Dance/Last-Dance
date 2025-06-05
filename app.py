from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from routes.auth import auth_bp
from routes.auth import auth_bp
from routes.diary_routes import diary_bp
from routes.music_routes import music_bp
from routes.public import public_bp
from routes.profile import profile_bp

from routes.public import public_bp
from routes.profile import profile_bp

from spotipy.oauth2 import SpotifyOAuth
from config.settings import configure_app
from config.settings import configure_app


# .env 파일 로드
# .env 파일 로드
load_dotenv()
print(f"SPOTIFY_CLIENT_ID from app: {os.getenv('SPOTIFY_CLIENT_ID')}")
print(f"SPOTIFY_CLIENT_SECRET from app: {os.getenv('SPOTIFY_CLIENT_SECRET')}")
print(f"SPOTIFY_REDIRECT_URI from app: {os.getenv('SPOTIFY_REDIRECT_URI')}")
print(f"SPOTIFY_CLIENT_ID from app: {os.getenv('SPOTIFY_CLIENT_ID')}")
print(f"SPOTIFY_CLIENT_SECRET from app: {os.getenv('SPOTIFY_CLIENT_SECRET')}")
print(f"SPOTIFY_REDIRECT_URI from app: {os.getenv('SPOTIFY_REDIRECT_URI')}")

app = Flask(__name__)
CORS(app)
configure_app(app)  # settings.py의 설정 적용
configure_app(app)  # settings.py의 설정 적용

# Firebase 초기화
try:
    # Firebase 인증 키 파일 경로 (app.py와 같은 폴더에 위치)
    cred = credentials.Certificate("firebase-auth.json")
    firebase_admin.initialize_app(cred)
    print("✅ Firebase 초기화 완료")
except Exception as e:
    print(f"❌ Firebase 초기화 실패: {e}")
# Firebase 초기화
try:
    # Firebase 인증 키 파일 경로 (app.py와 같은 폴더에 위치)
    cred = credentials.Certificate("firebase-auth.json")
    firebase_admin.initialize_app(cred)
    print("✅ Firebase 초기화 완료")
except Exception as e:
    print(f"❌ Firebase 초기화 실패: {e}")

# Firestore 클라이언트
# Firestore 클라이언트
db = firestore.client()

# 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(diary_bp, url_prefix='/api/diary')
app.register_blueprint(music_bp, url_prefix='/api/music')
app.register_blueprint(public_bp)
app.register_blueprint(profile_bp)

# Firebase 설정 반환 엔드포인트
@app.route('/api/firebase-config')
# Firebase 설정 반환 엔드포인트
@app.route('/api/firebase-config')
def get_firebase_config():
    """프론트엔드에서 Firebase 설정을 가져올 수 있는 엔드포인트"""
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
# Spotify OAuth 설정
sp_oauth = SpotifyOAuth(
    client_id=app.config['SPOTIFY_CLIENT_ID'],
    client_secret=app.config['SPOTIFY_CLIENT_SECRET'],
    redirect_uri=app.config['SPOTIFY_REDIRECT_URI'],
    scope='user-read-private user-read-currently-playing user-read-recently-played'
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
    
    print("\nLast Dance 서버 시작중...")
    
    auth_url = sp_oauth.get_authorize_url()
    print("\n✅ Spotify 인증 URL (브라우저에서 열기):")
    print(auth_url)

    app.run(debug=True)
