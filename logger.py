import os
import json
from datetime import datetime

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()

# Spotify API credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def get_spotify_client():
    """Authenticate with Spotify and return a Spotipy client."""
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

def get_user_display_name(user_id):
    """Fetch a Spotify user's display name using their user ID."""
    sp = get_spotify_client()
    user_info = sp.user(user_id)
    return user_info['display_name']

def get_user_playlists(spotify_client, user_id):

    """Fetch all public playlists of a Spotify user given their user ID."""
    playlists = []
    response = spotify_client.user_playlists(user_id)
    while response:
        playlists.extend(response['items'])
        if response['next']:
            response = spotify_client.next(response)
        else:
            break
    return playlists

def get_playlist_info(spotify_client, playlist):
    playlist_info = {}
    playlist_info['name'] = playlist['name']
    playlist_info['description'] = playlist['description']
    playlist_info['snapshot_id'] = playlist['snapshot_id']
    playlist_info['playlist_id'] = playlist['id']
    
    songs_info = []
    results = spotify_client.playlist_tracks(playlist_info['playlist_id'])
    while results:
        for track in results['items']:
            track_info = {}

            track_info['added_at'] = track['added_at']

            if playlist['collaborative']:
                adder_id = track['added_by']['id']
                adder_name = get_user_display_name(adder_id)
                track_info['added_by'] = adder_name

            track_info['song_name'] = track['track']['name']
            track_info['artist_name'] = track['track']['artists'][0]['name']
            
            songs_info.append(track_info)
        
        if results['next']:
            results = spotify_client.next(results)
        else:
            results = None

    playlist_info['songs'] = songs_info
    return playlist_info

def update_user_dir(parent_dir, user):
    user_name = sanitize_for_filename(user['display_name']) + '_'
    user_id = user['id']
    # Ensure the 'data' directory exists
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    
    # Define the full path for the new or existing user directory within 'data'
    user_dir_path = os.path.join(parent_dir, f"{user_name}{user_id}")

    # If the directory for the user exists with their current display_name, there's no need to change anything
    if os.path.exists(user_dir_path):
        return user_dir_path
    
    # Check if a directory for this user_id exists under a different name in the 'data' directory
    items = os.listdir(parent_dir)
    directories = [item for item in items if os.path.isdir(os.path.join(parent_dir, item))]
    matching_directories = [directory for directory in directories if directory.endswith(user_id)]

    # If there is no directory existing for user_id in 'data', make one
    # otherwise, rename the existing directory to match the updated user_name
    if not matching_directories:
        os.mkdir(user_dir_path)
    else:
        old_dir_path = os.path.join(parent_dir, matching_directories[0])
        os.rename(old_dir_path, user_dir_path)
        print(f"Directory renamed from {matching_directories[0]} to {os.path.basename(user_dir_path)}")
    return user_dir_path

def compare_data_and_log_changes(old_data, new_data):
    """Compare two dictionaries and return a list describing the differences."""
    changes = []
    for key in old_data:
        if key not in new_data:
            changes.append(f"Removed key: {key}, value was {old_data[key]}")
        elif old_data[key] != new_data[key]:
            changes.append(f"Changed key: {key}, from {old_data[key]} to {new_data[key]}")
    for key in new_data:
        if key not in old_data:
            changes.append(f"Added key: {key}, value is {new_data[key]}")
    return changes

def sanitize_for_filename(name, replacement="#"):
    """
    Sanitize a string to make it safe for use as a filename.
    Replaces invalid filesystem characters with a specified replacement character.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, replacement)
    return name

def log_changes_and_update_json(data_map, json_file_path):
    # Ensure directory exists
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    # Sanitize the filename part of json_file_path if necessary
    directory, filename = os.path.split(json_file_path)
    sanitized_filename = sanitize_for_filename(filename)
    sanitized_json_file_path = os.path.join(directory, sanitized_filename)
    
    existing_data = {}
    if os.path.exists(sanitized_json_file_path):
        with open(sanitized_json_file_path, 'r', encoding='utf-8') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = {}

    if existing_data != data_map:
        changes = compare_data_and_log_changes(existing_data, data_map)
        with open(sanitized_json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data_map, file, indent=4, ensure_ascii=False)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        changes_log_path = os.path.join(os.path.dirname(sanitized_json_file_path), 'changes.txt')
        with open(changes_log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{now} - Updated '{os.path.basename(sanitized_json_file_path)}':\n")
            for change in changes:
                log_file.write(f"    {change}\n")
        print("Changes logged and JSON file updated.")

def scrape(spotify_client, user_id):
    user = spotify_client.user(user_id)

    #update the directory for user_id
    parent_dir = os.path.join(os.getcwd(), 'data')
    user_path = update_user_dir(parent_dir, user)

    user_json_path = os.path.join(user_path,'account_info')
    log_changes_and_update_json(user, user_json_path)
    
    user_playlists = get_user_playlists(spotify_client,user_id)
    
    for playlist in user_playlists:
        playlist['name'] = sanitize_for_filename(playlist['name'])
        playlist_path = os.path.join(user_path, str(playlist['name'] + '_' + playlist['id']))
        #print("playlist: ",playlist['name'])

        playlist_info = get_playlist_info(spotify_client,playlist)
        log_changes_and_update_json(playlist_info,playlist_path)

def main():
    spotify_client = get_spotify_client()
    user_ids = ['va2q7gdf2g9q73ncsvr1m3snz','imdzcwxqs1zwms4tq1fvwg0rl']
    for user_id in user_ids:
        user = spotify_client.user(user_id)
        print("User: ",user['display_name'])
        scrape(spotify_client,user_id)

if __name__ == "__main__":
    main()    