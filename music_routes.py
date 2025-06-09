from flask import Blueprint, request, jsonify, current_app
import spotipy
from spotipy.oauth2 import SpotifyOAuth

music_bp = Blueprint('music', __name__)

# Spotify API 설정
def get_spotify_client():
    """현재 애플리케이션의 설정에서 Spotify 클라이언트를 생성하는 함수"""
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=current_app.config['SPOTIFY_CLIENT_ID'],
        client_secret=current_app.config['SPOTIFY_CLIENT_SECRET'],
        redirect_uri=current_app.config['SPOTIFY_REDIRECT_URI'],
        scope='user-read-private'
    ))

def search_spotify_tracks(query, limit=5):
    sp = get_spotify_client()
    results = sp.search(q=query, type='track', limit=limit)
    tracks = []
    for item in results['tracks']['items']:
        tracks.append({
            'title': item['name'],
            'artist': item['artists'][0]['name'],
            'url': item['external_urls']['spotify']
        })
    return tracks

@music_bp.route('/recommend', methods=['POST'])
def recommend_music():
    data = request.json
    emotion = data.get('emotion')

    # 감정에 따른 장르 매핑
    genre_map = {
        'joy': 'happy pop',
        'sadness': 'sad ballad',
        'anger': 'hard rock',
        'fear': 'ambient',
        'neutral': 'lofi'
    }

    query = genre_map.get(emotion, 'pop')

    try:
        spotify_tracks = search_spotify_tracks(query)
        return jsonify({
            'message': '음악 추천 성공!',
            'emotion': emotion,
            'recommendations': spotify_tracks
        })
    except Exception as e:
        return jsonify({'message': 'Spotify API 오류 발생', 'error': str(e)}), 500

    @music_bp.route('/page', methods=['GET'])
    def show_recommendation_page():
        return render_template('recommend_music.html')