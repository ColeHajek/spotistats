import os
import json
from datetime import datetime
from argparse import ArgumentParser
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from logger import scrape

def load_client():
    # Load environment variables
    load_dotenv()
    # Spotify API credentials
    return os.getenv('SPOTIFY_CLIENT_ID'), os.getenv('SPOTIFY_CLIENT_SECRET')

class options:
    mode: str = "scrape"
    user_id: str = "va2q7gdf2g9q73ncsvr1m3snz"


if __name__ == '__main__':
    
    # load dataclass arguments from yml file
    
    config = options()
    parser = ArgumentParser()

    parser.add_argument("--mode", type=str, help="The model to initialize.", default=config.mode)

    if config.mode == "rec":
        placehoder = 1

    parser.add_argument("--user_id", type=float, help="The end part of the link to the users profile ex: https://open.spotify.com/user/<user_id>", default=config.user_id)