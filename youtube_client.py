import os, json, pickle

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from youtube_dl import YoutubeDL

import constants

class YoutubeClient:
    def __init__(self):
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.credentials = self.init_credentials()
        self.client = self.init_youtube_client()        

    def init_credentials(self):
        if not os.path.isfile(constants.YOUTUBE_AUTH_PICKLE):
            return

        with open(constants.YOUTUBE_AUTH_PICKLE) as creds:
            return pickle.load(creds)

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
            "refresh_token": self.credentials.refresh_token
        }

        with open(constants.YOUTUBE_AUTH_PICKLE, "wb") as creds:
            pickle.dump(self.credentials, creds)

        with open("youtube_secrets.json", "w") as secrets:
            json.dump(youtube_tokens, secrets)

        self.client = build(
            self.api_service_name,
            self.api_version,
            credentials=self.credentials
        )

    def get_liked_videos(self, pageToken = None):
        request = self.client.videos().list(
            part="snippet",
            maxResults=10,
            myRating="like",
            pageToken=pageToken,
            fields="items(id,snippet.title),nextPageToken"
        )

        return request.execute()

    def get_valid_songs(self, response):
        valid_songs = {}

        for item in response["items"]:
            title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"]
            )

            try:
                video = YoutubeDL({}).extract_info(youtube_url, download=False)
            except:
                continue

            song_name = video["track"]
            artist = video["artist"]

            if song_name and artist:
                valid_songs[title] = {
                    "title": song_name,
                    "artist": artist
                }

        return valid_songs
