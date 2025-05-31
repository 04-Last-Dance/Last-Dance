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

# Firebase 초기화
try:
    # Firebase 인증 키 파일 경로 (app.py와 같은 폴더에 위치)
    cred = credentials.Certificate("firebase-auth.json")
    firebase_admin.initialize_app(cred)
    print("✅ Firebase 초기화 완료")
except Exception as e:
    print(f"❌ Firebase 초기화 실패: {e}")

# Firestore 클라이언트
db = firestore.client()



# 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(diary_bp, url_prefix='/api/diary')
app.register_blueprint(music_bp, url_prefix='/api/music')
app.register_blueprint(public_bp)



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
    """Spotify OAuth 콜백 처리"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        print(f"❌ Spotify 인증 오류: {error}")
        return redirect('/?error=spotify_auth_failed')
    
    try:
        token_info = sp_oauth.get_access_token(code)
        print("✅ Spotify 토큰 획득 성공")
        # 토큰 정보를 세션이나 데이터베이스에 저장할 수 있습니다
        return redirect('/?success=spotify_connected')
    except Exception as e:
        print(f"❌ Spotify 토큰 획득 실패: {e}")
        return redirect('/?error=token_failed')

@app.route('/api/spotify/auth-url')
def get_spotify_auth_url():
    """Spotify 인증 URL 반환"""
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})

@app.route('/')
def index():
    """홈페이지"""
    return jsonify({
        "message": "Music Diary API Server",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth",
            "diary": "/api/diary", 
            "music": "/api/music",
            "firebase_config": "/api/firebase-config",
            "spotify_auth": "/api/spotify/auth-url"
        }
    })

@app.route('/health')
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "firebase": "connected" if firebase_admin._apps else "disconnected",
        "spotify": "configured" if os.getenv('SPOTIFY_CLIENT_ID') else "not_configured"
    })

if __name__ == '__main__':
    print("\n🎵 Music Diary 서버 시작중...")
    
    # 환경변수 체크
    required_env_vars = [
        'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI',
        'FIREBASE_API_KEY', 'FIREBASE_AUTH_DOMAIN', 'FIREBASE_PROJECT_ID'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"⚠️  누락된 환경변수: {', '.join(missing_vars)}")
        print("💡 .env 파일을 확인해주세요!")
    
    # Spotify 인증 URL 출력
    try:
        auth_url = sp_oauth.get_authorize_url()
        print(f"\n✅ Spotify 인증 URL:")
        print(f"🔗 {auth_url}")
        print("\n📝 브라우저에서 위 URL을 열어 Spotify 인증을 완료하세요!")
    except Exception as e:
        print(f"❌ Spotify OAuth 설정 오류: {e}")
    
    print(f"\n🚀 서버 실행 중: http://localhost:5000")
    print(f"📊 API 문서: http://localhost:5000")
    print(f"💗 헬스 체크: http://localhost:5000/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)