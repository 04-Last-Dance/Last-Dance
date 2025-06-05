import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

def configure_app(app):
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    app.config['SPOTIFY_CLIENT_ID'] = os.getenv('SPOTIFY_CLIENT_ID')
    print(f"SPOTIFY_CLIENT_ID in settings: {app.config['SPOTIFY_CLIENT_ID']}")
    app.config['SPOTIFY_CLIENT_SECRET'] = os.getenv('SPOTIFY_CLIENT_SECRET')
    app.config['SPOTIFY_REDIRECT_URI'] = os.getenv('SPOTIFY_REDIRECT_URI')