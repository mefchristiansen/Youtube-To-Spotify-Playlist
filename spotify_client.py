import os, json

import spotipy
from spotipy import oauth2

class SpotifyClient:
    def __init__(self):
        self.scope = "playlist-modify-public"
        self.client = self.init_spotify_client()        

    def init_spotify_client(self):
        if not os.path.isfile('spotify_secrets.json'):
            return

        with open('spotify_secrets.json') as f:
            spotify_tokens = json.load(f)

        return spotipy.Spotify(auth=spotify_tokens["access_token"])

    def refresh(self):
        if not os.path.isfile('spotify_secrets.json'):
            return

        with open('spotify_secrets.json') as f:
            spotify_tokens = json.load(f)

        sp_oauth = oauth2.SpotifyOAuth(
            client_id=spotify_tokens["client_id"],
            client_secret=spotify_tokens["client_secret"],
            redirect_uri=spotify_tokens["redirect_uri"],
            scope=self.scope
        )

        token_info = sp_oauth.refresh_access_token(spotify_tokens['refresh_token'])

        spotify_tokens["access_token"] = token_info["access_token"]
        spotify_tokens["refresh_token"] = token_info["refresh_token"]

        with open('spotify_secrets.json', 'w') as f:
            json.dump(spotify_tokens, f)

        self.client= spotipy.Spotify(auth=token_info["access_token"])
        