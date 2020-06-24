import os

import json

import boto3

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import spotipy

def main():
    youtube_client = init_youtube_client()
    spotify_client = init_spotify_client()

    return

def init_youtube_client():
    if not os.path.isfile('youtube_secrets.json'):
        return

    with open('youtube_secrets.json') as f:
        youtube_tokens = json.load(f)

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

def init_spotify_client():
    if not os.path.isfile('spotify_secrets.json'):
        return

    with open('spotify_secrets.json') as f:
        spotify_tokens = json.load(f)

    return spotipy.Spotify(auth=spotify_tokens["access_token"])

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




    
