import os, json, pickle

from urllib.error import HTTPError

import spotipy
from spotipy import oauth2

import constants

class SpotifyClient:
    def __init__(self):
        self.scope = "playlist-modify-public"
        self.sp_oauth = self.init_spotify_oauth()
        self.client = self.init_spotify_client()

    def init_spotify_oauth(self):
        if not os.path.isfile(constants.SPOTIFY_AUTH_PICKLE):
            print("[ERROR] Spotify auth pickle file does exist. Please run the set up script (set_up.py) first.")
            return

        with open(constants.SPOTIFY_AUTH_PICKLE, "rb") as creds:
            return pickle.load(creds)

    def init_spotify_client(self):
        if not os.path.isfile(constants.SPOTIFY_SECRETS):
            return

        with open(constants.SPOTIFY_SECRETS) as f:
            spotify_secrets = json.load(f)

        return spotipy.Spotify(auth=spotify_secrets["access_token"])

    def refresh(self):
        if not os.path.isfile(constants.SPOTIFY_SECRETS):
            return

        with open(constants.SPOTIFY_SECRETS) as f:
            spotify_secrets = json.load(f)

        token_info = self.sp_oauth.refresh_access_token(
            spotify_secrets['refresh_token']
        )

        spotify_secrets["access_token"] = token_info["access_token"]
        spotify_secrets["refresh_token"] = token_info["refresh_token"]

        with open(constants.SPOTIFY_SECRETS, 'w') as f:
            json.dump(spotify_secrets, f)

        self.client = spotipy.Spotify(auth=token_info["access_token"])

    def get_playlist(self):
        if not os.path.isfile(constants.SPOTIFY_SECRETS):
            return

        with open(constants.SPOTIFY_SECRETS) as f:
            spotify_secrets = json.load(f)

        playlist_id = spotify_secrets["playlist_id"]

        if playlist_id:
            try:
                playlist = self.client.playlist(playlist_id)
                return playlist['id']
            except HTTPError:
                return self.create_playlist()
        else:
            return self.create_playlist()

    def create_playlist(self):
        user_id = self.client.me()['id']

        response = self.client.user_playlist_create(
            user=user_id, 
            name="Youtube Liked Songs",
            public=True,
            description="My Youtube liked songs"
        )

        if not os.path.isfile(constants.SPOTIFY_SECRETS):
            return

        with open(constants.SPOTIFY_SECRETS) as f:
            spotify_secrets = json.load(f)
        
        spotify_secrets["playlist_id"] = response["id"]

        with open(constants.SPOTIFY_SECRETS, 'w') as f:
            json.dump(spotify_secrets, f)

        return spotify_secrets["playlist_id"]

    def add_songs_to_playlist(self, songs, playlist_id, existing_track_uris):
        if not songs:
            return

        track_uris = []

        for song in songs:
            search_results = self.client.search(
                self.format_query(
                    song["title"],
                    song["artist"]
                )
            )

            tracks = search_results["tracks"]["items"]

            if not tracks:
                continue

            track_uri = tracks[0]["uri"]

            if track_uri in existing_track_uris:
                print("Track already in playlist")
                continue

            track_uris.append(track_uri)

        if not track_uris:
            return

        user_id = self.client.me()['id']

        self.client.user_playlist_add_tracks(
            user_id,
            playlist_id,
            track_uris
        )

    def format_query(self, title, artist):
        return "{track} artist:{artist}".format(
            track = title,
            artist = artist
        )

    def get_existing_tracks(self, playlist_id):
        track_uris = []
        user_id = self.client.me()['id']

        playlist = self.client.user_playlist(
            user_id,
            playlist_id
        )

        while playlist:
            for track in playlist["tracks"]["items"]:
                track_uris.append(track["track"]['uri'])
            if playlist["tracks"]["next"]:
                playlist = self.client.next(playlist["tracks"])
            else:
                playlist = None

        return track_uris
