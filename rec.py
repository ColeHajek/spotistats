import os
import json
from datetime import datetime

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

generas = [
        "acoustic", "afrobeat", "alt-rock", "alternative",
        "ambient", "anime", "black-metal", "bluegrass",
        "blues", "bossanova", "brazil", "breakbeat",
        "british", "cantopop", "chicago-house", 
        "children", "chill", "classical", "club",
        "comedy", "country", "dance", "dancehall", 
        "death-metal", "deep-house", "detroit-techno",
        "disco", "disney", "drum-and-bass", "dub",
        "dubstep", "edm", "electro", "electronic",
        "emo", "folk", "forro", "french", "funk", 
        "garage", "german", "gospel", "goth", "grindcore",
        "groove", "grunge", "guitar", "happy", "hard-rock",
        "hardcore", "hardstyle", "heavy-metal", "hip-hop",
        "holidays", "honky-tonk", "house", "idm", "indian", 
        "indie", "indie-pop", "industrial", "iranian", "j-dance",
        "j-idol", "j-pop", "j-rock", "jazz", "k-pop", "kids", 
        "latin", "latino", "malay", "mandopop", "metal", 
        "metal-misc", "metalcore", "minimal-techno", "movies", 
        "mpb", "new-age", "new-release", "opera", "pagode", 
        "party", "philippines-opm", "piano", "pop", "pop-film", 
        "post-dubstep", "power-pop", "progressive-house", "psych-rock", 
        "punk", "punk-rock", "r-n-b", "rainy-day", "reggae", "reggaeton", 
        "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad", 
        "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", 
        "ska", "sleep", "songwriter", "soul", "soundtracks", "spanish",
        "study", "summer", "swedish", "synth-pop", "tango", "techno", 
        "trance", "trip-hop", "turkish", "work-out", "world-music"
        ]

class settings:
    mode: str = 'playlist'

class params:
    
    seed_generas = []
    seed_artists = []
    seed_tracks = []
    
load_dotenv()

# Spotify API credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'playlist-modify-public playlist-modify-private'

def get_spotify_client():
    """Authenticate with Spotify and return a Spotipy client authorized to act on behalf of a user."""
    auth_manager = SpotifyOAuth(client_id=CLIENT_ID,
                                client_secret=CLIENT_SECRET,
                                redirect_uri=REDIRECT_URI,
                                scope=SCOPE)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp


def get_custom_recommendations(spotify_client, seed_genres=None, seed_artists=None, seed_tracks=None, feature_targets=None, limit=20):
    # Example feature_targets: {'energy': 0.8, 'danceability': 0.7, 'acousticness': 0.3}
    params = {
        'limit': limit,
        'seed_genres': seed_genres,
        'seed_artists': seed_artists,
        'seed_tracks': seed_tracks,
    }
    # Add target features to params if provided
    if feature_targets:
        for feature, target in feature_targets.items():
            params[f'target_{feature}'] = target
    
    recommendations = spotify_client.recommendations(**params)
    return recommendations['tracks']

def get_recommendations(spotify_client, seed_tracks, limit=20):
    recommendations = spotify_client.recommendations(seed_tracks=seed_tracks, limit=limit)
    return recommendations['tracks']

def get_playlist_tracks(spotify_client, playlist_id):
    tracks = []
    results = spotify_client.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = spotify_client.next(results)
        tracks.extend(results['items'])
    return tracks


#default
def create_recommended_playlist(spotify_client, original_playlist_id, new_playlist_name, user_id,num_songs):
    original_tracks = get_playlist_tracks(spotify_client, original_playlist_id)
    seed_tracks = [track['track']['id'] for track in original_tracks[-5:]]  # Use the first 5 tracks as seeds

    # Fetch recommendations based on the seed tracks
    recommended_tracks = get_recommendations(spotify_client, seed_tracks, num_songs)
    
    # Create a new playlist
    new_playlist = spotify_client.user_playlist_create(user_id, new_playlist_name)
    new_playlist_id = new_playlist['id']
    
    # Add recommended tracks to the new playlist
    track_uris = [track['uri'] for track in recommended_tracks]
    spotify_client.playlist_add_items(new_playlist_id, track_uris)

    return new_playlist_id

def main():
    spotify_client = get_spotify_client()
#
    user_id = 'va2q7gdf2g9q73ncsvr1m3snz'
    playlist_id = '3A8Dl74kAiYBf3KNHdQnop'
    
    create_recommended_playlist(spotify_client,playlist_id,"API_ML_playlist_suggestions_test4",user_id,10)

if __name__ == "__main__":
    main()
    