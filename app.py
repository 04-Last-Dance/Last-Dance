from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from routes.auth_routes import auth_bp
from routes.diary_routes import diary_bp
from routes.music_routes import music_bp
from spotipy.oauth2 import SpotifyOAuth

# .env 읽어오기
load_dotenv()

app = Flask(__name__)
CORS(app)

# Firebase 인증 키 파일 경로
cred = credentials.Certificate("firebase-auth.json")
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 사용
db = firestore.client()

# 블루프린트 등록
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(diary_bp, url_prefix='/api/diary')
app.register_blueprint(music_bp, url_prefix='/api/music')

def get_firebase_config():
    config = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID')
    }
    return jsonify(config)

sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
    scope='user-read-private'
)

@app.route('/callback')
def spotify_callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    return redirect('/')  # 성공 후 리디렉트할 페이지

if __name__ == '__main__':
    # Spotify 인증 URL 강제 출력
    auth_url = sp_oauth.get_authorize_url()
    print("\n✅ Spotify 인증 URL (브라우저에서 열기):")
    print(auth_url)

    app.run(debug=True)
