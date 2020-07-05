import os

import spotipy
from spotipy import oauth2

import constants

from parameter_store import ParameterStore

class SpotifyClient:
    """
        The Spotify client class used to interface with the Spotify Web API.
    """

    def __init__(self):
        # The scope of permissions request from the user
        self._scope = "playlist-modify-public"
        # Parameter store to get and update Spotify secrets
        self._parameter_store = ParameterStore('Spotify', constants.SPOTIFY_SECRETS)
        self._sp_oauth = self._init_spotify_oauth()
        self._client = self._init_spotify_client()

    def _init_spotify_oauth(self):
        """
            Instantiates and returns a SpotifyOAuth object. This is used to
            refresh the Spotify access token on expiration.
        """

        spotify_secrets = self._parameter_store.get_secrets()

        return oauth2.SpotifyOAuth(
            client_id=spotify_secrets.get("client_id"),
            client_secret=spotify_secrets.get("client_secret"),
            redirect_uri=spotify_secrets.get("redirect_uri"),
            scope=self._scope
        )

    def _init_spotify_client(self):
        """
            Instantiates and returns a Spotify Web API client.
        """

        spotify_secrets = self._parameter_store.get_secrets()
        return spotipy.Spotify(auth=spotify_secrets.get("access_token"))

    def refresh(self):
        """
            Refreshes the Spotify access token.
        """

        spotify_secrets = self._parameter_store.get_secrets()

        token_info = self._sp_oauth.refresh_access_token(
            spotify_secrets.get('refresh_token')
        )

        self._parameter_store.update_secrets({
            "access_token": token_info["access_token"],
            "refresh_token": token_info["refresh_token"]
        })

        self._client = spotipy.Spotify(auth=token_info.get("access_token"))

    def get_playlist(self):
        """
            Returns the playlist id of the user's "Youtube Liked Videos"
            playlist on Spotify
        """

        spotify_secrets = self._parameter_store.get_secrets()

        playlist_id = spotify_secrets.get("playlist_id")

        if playlist_id:
            # If a playlist parameter exists, check to see that it exists
            # in the user's spotify and return its id
            try:
                playlist = self._client.playlist(playlist_id)
                return playlist['id']
            except spotipy.exceptions.SpotifyException:
                # If there is an exception (i.e. the playlist does not exist),
                # create it and return its id
                return self._create_playlist()
        else:
            # If the playlist does not exist, create it and return its id
            return self._create_playlist()

    def _create_playlist(self):
        """
            Creates a new Spotify playlist and returns its id
        """

        user_id = self._client.me()['id']

        response = self._client.user_playlist_create(
            user=user_id, 
            name="Youtube Liked Songs",
            public=False,
            description="My Youtube liked songs"
        )

        playlist_id = response["id"]
        
        self._parameter_store.update_secrets({
            "playlist_id": playlist_id
        })

        return playlist_id

    def add_songs_to_playlist(self, songs, playlist_id, existing_track_uris):
        """
            Adds the provided tracks to the provided playlist
        """

        if not songs:
            return

        track_uris = []

        for song in songs:
            # Query the Spotify API for the current track
            search_results = self._client.search(
                self._format_query(
                    song["title"],
                    song["artist"]
                )
            )

            tracks = search_results["tracks"]["items"]

            if not tracks:
                # If the track could not be found on Spotify, continue
                continue

            track_uri = tracks[0]["uri"]

            if track_uri in existing_track_uris:
                # If the track already exists in the playlist, continue
                print("Track already in playlist")
                continue

            track_uris.append(track_uri)

        if not track_uris:
            return

        user_id = self._client.me()['id']

        self._client.user_playlist_add_tracks(
            user_id,
            playlist_id,
            track_uris
        )

    def _format_query(self, title, artist):
        """
            Formats the track query for the Spotify API
        """

        return "{track} artist:{artist}".format(
            track = title,
            artist = artist
        )

    def get_existing_tracks(self, playlist_id):
        """
            Returns the uris of all the tracks currently in the playlist
        """

        track_uris = []
        user_id = self._client.me()['id']

        playlist = self._client.user_playlist(
            user_id,
            playlist_id
        )

        while playlist:
            # Iterate through all pages of track results from the playlist
            for track in playlist["tracks"]["items"]:
                track_uris.append(track["track"]['uri'])
            if playlist["tracks"]["next"]:
                playlist = self._client.next(playlist["tracks"])
            else:
                playlist = None

        return track_uris     