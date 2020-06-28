import os, json

import spotipy

from youtube_client import YoutubeClient
from spotify_client import SpotifyClient

def main():
    youtube_client = YoutubeClient()
    spotify_client = SpotifyClient()

    # Refresh tokens for both clients
    youtube_client.refresh()
    spotify_client.refresh()

    # Get Spotify playlist id
    playlist_id = spotify_client.get_playlist()

    # Get uris of tracks already in the Spotify playlist
    existing_track_uris = spotify_client.get_existing_tracks(playlist_id)

    # Get recent video id
    recent_video_id = youtube_client.get_recent_video_id()
    recent_video_id_updated = False

    # Get first page of Youtube liked videos
    res = youtube_client.get_liked_videos()

    while res:
        # Get Youtube Valid Songs
        songs, already_processed = youtube_client.get_valid_songs(res, recent_video_id)

        # Add songs to playlist
        try:
            spotify_client.add_songs_to_playlist(
                songs,
                playlist_id,
                existing_track_uris
            )
        except spotipy.exceptions.SpotifyException as err:
            # Catch Spotify client error
            if err.http_status == 401 and 'access token expired' in err.msg:
                # If the access token has expired, refresh it and continue
                spotify_client.refresh()
                continue
            else:
                print("[ERROR] There was an unexpected error with the Spotify client.")
                print(err)
                break

        if not recent_video_id_updated:
            youtube_client.store_recent_video_id(res["items"][0]["id"])
            recent_video_id_updated = True

        if already_processed or 'nextPageToken' not in res:
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




    
