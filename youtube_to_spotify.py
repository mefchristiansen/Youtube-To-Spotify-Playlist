import os

import json

import boto3

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def main():
    if not os.path.isfile('secrets.json'):
        return

    with open('secrets.json') as f:
        secrets = json.load(f)

    youtube_client = init_youtube_client(secrets["youtube"])
    return

def init_youtube_client(youtube_tokens):
    api_service_name = "youtube"
    api_version = "v3"

    credentials = Credentials(
        youtube_tokens['access_token'],
        refresh_token=youtube_tokens['refresh_token'],
        token_uri=youtube_tokens['token_uri'],
        client_id=youtube_tokens['client_id'],
        client_secret=youtube_tokens['client_secret']
    )

    return build(api_service_name, api_version, credentials=credentials)

def get_liked_videos(youtube_client):
    request = youtube_client.videos().list(
        part="snippet,contentDetails,statistics",
        myRating="like"
    )

    response = request.execute()

# def refresh():
#     credentials.refresh(Request())


if __name__ == "__main__":
    main()




    
