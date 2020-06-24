import os, json

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from youtube_dl import YoutubeDL

class YoutubeClient:
    def __init__(self):
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.credentials = self.init_credentials()
        self.client = self.init_youtube_client()        

    def init_credentials(self):
        if not os.path.isfile('youtube_secrets.json'):
            return

        with open('youtube_secrets.json') as f:
            youtube_tokens = json.load(f)

        return Credentials(
            youtube_tokens['access_token'],
            refresh_token=youtube_tokens['refresh_token'],
            token_uri=youtube_tokens['token_uri'],
            client_id=youtube_tokens['client_id'],
            client_secret=youtube_tokens['client_secret']
        )

    def init_youtube_client(self):
        return build(
            self.api_service_name,
            self.api_version,
            credentials=self.credentials
        )

    def refresh(self):
        self.credentials.refresh(Request())

        youtube_tokens = {
            "access_token": self.credentials.token,
            "refresh_token": self.credentials.refresh_token,
            "token_uri": self.credentials.token_uri,
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret
        }

        with open('youtube_secrets.json', 'w') as f:
            json.dump(youtube_tokens, f)

        self.client = build(
            self.api_service_name,
            self.api_version,
            credentials=self.credentials
        )

    def get_liked_videos(self):
        request = self.client.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like"
        )

        return request.execute()

    def get_valid_songs(self):
        response = self.get_liked_videos()

        valid_songs = {}

        for item in response["items"]:
            title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["id"])

            video = YoutubeDL({}).extract_info(youtube_url, download=False)
            song_name = video["track"]
            artist = video["artist"]

            if song_name and artist:
                valid_songs[title] = {
                    "song_name": song_name,
                    "artist": artist
                }

        return valid_songs
