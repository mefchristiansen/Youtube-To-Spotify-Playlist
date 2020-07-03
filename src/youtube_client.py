import os, json, pickle

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from youtube_dl import YoutubeDL

import constants

from parameter_store import ParameterStore

class YoutubeClient:
    def __init__(self):
        self._api_service_name = "youtube"
        self._api_version = "v3"
        self._scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        self._parameter_store = ParameterStore('Youtube', constants.YOUTUBE_SECRETS)
        self._credentials = self._init_credentials()
        self._client = self._init_youtube_client()

    def _init_credentials(self):
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
        return build(
            self._api_service_name,
            self._api_version,
            credentials=self._credentials,
            cache_discovery=False
        )

    def refresh(self):
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
        request = self._client.videos().list(
            part="snippet",
            maxResults=10,
            myRating="like",
            pageToken=pageToken,
            fields="items(id,snippet.title),nextPageToken"
        )

        return request.execute()

    def get_valid_songs(self, response, recent_video_id):
        valid_songs = []
        already_processed = False

        youtube_dl_outtmpl = {}

        env = os.environ.get('ENV')
        if env == "production":
            youtube_dl_outtmpl['outtmpl'] = "/tmp/%(id)s%(ext)s"

        print("OUTTMPL")
        print(youtube_dl_outtmpl)

        for item in response["items"]:            
            if item["id"] == recent_video_id:
                already_processed = True
                break

            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"]
            )

            try:
                video = YoutubeDL({'outtmpl': '/tmp/%(id)s%(ext)s'}).extract_info(
                    youtube_url,
                    download=False
                )
            except:
                continue

            song_name = video["track"]
            artist = video["artist"]

            if song_name and artist:
                valid_songs.append ({
                    "title": song_name,
                    "artist": artist
                })

        return valid_songs, already_processed

    def store_recent_video_id(self, video_id):
        self._parameter_store.update_secrets({
            "recent_video_id": video_id
        })

    def get_recent_video_id(self):
        youtube_secrets = self._parameter_store.get_secrets()
        return youtube_secrets.get("recent_video_id")