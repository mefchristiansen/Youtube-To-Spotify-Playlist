import os

from googleapiclient.discovery import build
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from youtube_dl import YoutubeDL

import constants

from parameter_store import ParameterStore

class YoutubeClient:
    """
        The Youtube client class used to interface with the Youtube API.
    """

    def __init__(self):
        self._api_service_name = "youtube"
        self._api_version = "v3"
        # The scopes of permissions request from the user
        self._scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        # Parameter store to get and update Spotify secrets
        self._parameter_store = ParameterStore('Youtube', constants.YOUTUBE_SECRETS)
        self._credentials = self._init_credentials()
        self._client = self._init_youtube_client()

    def _init_credentials(self):
        """
            Instantiates and returns a Credentials object. This is used to
            instantiate the Youtube API client, and to refresh the Youtube
            access token on expiration.
        """

        youtube_secrets = self._parameter_store.get_secrets()

        return Credentials (
            token=youtube_secrets.get("access_token"),
            refresh_token=youtube_secrets.get("refresh_token"),
            token_uri=youtube_secrets.get("token_uri"),
            client_id=youtube_secrets.get("client_id"),
            client_secret=youtube_secrets.get("client_secret"),
            scopes=self._scopes
        )

    def _init_youtube_client(self):
        """
            Instantiates and returns a Youtube API client.
        """

        return build(
            self._api_service_name,
            self._api_version,
            credentials=self._credentials,
            cache_discovery=False
        )

    def refresh(self):
        """
            Refreshes the Youtube access token.
        """

        self._credentials.refresh(Request())

        self._parameter_store.update_secrets({
            "access_token": self._credentials.token,
            "refresh_token": self._credentials.refresh_token
        })

        self._client = build(
            self._api_service_name,
            self._api_version,
            credentials=self._credentials
        )

    def get_liked_videos(self, pageToken = None):
        """
            Returns the provided page of the user's liked Youtube videos 
        """

        request = self._client.videos().list(
            part="snippet",
            maxResults=10,
            myRating="like",
            pageToken=pageToken,
            fields="items(id,snippet.title),nextPageToken"
        )

        return request.execute()

    def get_valid_songs(self, response, recent_video_id):
        """
            Iterates through the provided liked videos response from the Youtube
            API, and uses YoutubeDL to parse out the videos that are music
            tracks.
        """

        valid_songs = []
        already_processed = False

        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True
        }

        for item in response["items"]:            
            if item["id"] == recent_video_id:
                print("[NOTICE] Reached already processed video.")
                already_processed = True
                break

            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"]
            )

            try:
                # Get a Youtube video's info
                video = YoutubeDL(ydl_opts).extract_info(
                    youtube_url,
                    download=False
                )
            except:
                continue

            song_name = video["track"]
            artist = video["artist"]

            if song_name and artist:
                # If the video is a music track, add it to the valid songs array
                valid_songs.append ({
                    "title": song_name,
                    "artist": artist
                })

        return valid_songs, already_processed

    def store_recent_video_id(self, video_id):
        """
            Stores the video id of the most recently liked video.
        """

        self._parameter_store.update_secrets({
            "recent_video_id": video_id
        })

    def get_recent_video_id(self):
        """
            Returns the video id of the most recently liked video.
        """

        youtube_secrets = self._parameter_store.get_secrets()
        return youtube_secrets.get("recent_video_id")