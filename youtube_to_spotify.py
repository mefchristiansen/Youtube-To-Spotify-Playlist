import os

import json

import boto3

from youtube_client import YoutubeClient
from spotify_client import SpotifyClient

def main():
    youtube_client = YoutubeClient()
    spotify_client = SpotifyClient()

    return

def get_liked_videos(youtube_client):
    request = youtube_client.videos().list(
        part="snippet,contentDetails,statistics",
        myRating="like"
    )

    response = request.execute()




if __name__ == "__main__":
    main()




    
