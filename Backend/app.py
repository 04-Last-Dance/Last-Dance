from flask import Flask, request, redirect
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.diary_routes import diary_bp
from routes.music_routes import music_bp
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
CORS(app)

# 블루프린트 등록
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(diary_bp, url_prefix='/api/diary')
app.register_blueprint(music_bp, url_prefix='/api/music')

# Spotify OAuth 설정
SPOTIFY_CLIENT_ID = 'ceed4f973932401db4c3145c4b8c4bd4'
SPOTIFY_CLIENT_SECRET = '160fad0db2c942b7a76a541ebb61fd52'
SPOTIFY_REDIRECT_URI = 'https://595f-211-244-170-176.ngrok-free.app/callback'

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
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
