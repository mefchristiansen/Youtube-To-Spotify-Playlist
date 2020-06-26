import os, json

import spotipy

from youtube_client import YoutubeClient
from spotify_client import SpotifyClient

def main():
    youtube_client = YoutubeClient()
    spotify_client = SpotifyClient()

    # Refresh access tokens for both clients
    youtube_client.refresh()
    spotify_client.refresh()

    # Get Spotify Playlist
    playlist_id = spotify_client.get_playlist()

    # Get uris of tracks already in playlist
    existing_track_uris = spotify_client.get_existing_tracks(playlist_id)

    res = youtube_client.get_liked_videos()

    while res:
        # Get Youtube Valid Songs
        songs = youtube_client.get_valid_songs(res)

        # Add songs to playlist
        try:
            spotify_client.add_songs_to_playlist(
                songs,
                playlist_id,
                existing_track_uris
            )
        except spotipy.exceptions.SpotifyException as err:
            if err.http_status == 401 and 'access token expired' in err.msg:
                spotify_client.refresh()
                continue
            else:
                break

        if 'nextPageToken' not in res:
            break

        # Get next page of liked Youtube videos
        try:
            res = youtube_client.get_liked_videos(res['nextPageToken'])
        except:
            pass
            # youtube_client.refresh()
            # continue

    return

if __name__ == "__main__":
    main()




    
