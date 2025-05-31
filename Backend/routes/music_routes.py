# /BE/routes/music_routes.py

from flask import Blueprint, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

music_bp = Blueprint('music', __name__)

# Spotify API 설정
SPOTIFY_CLIENT_ID = 'ceed4f973932401db4c3145c4b8c4bd4'
SPOTIFY_CLIENT_SECRET = '160fad0db2c942b7a76a541ebb61fd52'
SPOTIFY_REDIRECT_URI = 'https://595f-211-244-170-176.ngrok-free.app/callback'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope='user-read-private'
))



def search_spotify_tracks(query, limit=5):
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
