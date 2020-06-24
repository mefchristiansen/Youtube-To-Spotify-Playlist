import os, json

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

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