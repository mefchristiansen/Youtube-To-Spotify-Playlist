import os

import json

import boto3

from youtube_client import YoutubeClient
from spotify_client import SpotifyClient

def main():
    youtube_client = YoutubeClient()
    spotify_client = SpotifyClient()

    # Get Youtube Valid Songs
    songs = youtube_client.get_valid_songs()

    # Get Spotify Playlist
    playlist_id = spotify_client.get_playlist()

    # Add songs to playlist
    spotify_client.add_songs_to_playlist(songs, playlist_id)

    return

if __name__ == "__main__":
    main()




    
