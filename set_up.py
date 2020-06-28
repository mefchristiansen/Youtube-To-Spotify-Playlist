import json, os, pickle

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from spotipy import oauth2

import constants

def main():
    set_up_youtube_tokens()
    set_up_spotify_token()

def set_up_youtube_tokens():
    client_secrets_file = constants.YOUTUBE_CLIENT_SECRETS
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    # Get credentials and create an API client
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )

    auth_url, _ = flow.authorization_url(prompt="consent")
    print("Please go to this URL: {}".format(auth_url))
    code = input("Enter the authorization code: ")
    flow.fetch_token(code=code)
    credentials = flow.credentials

    youtube_tokens = {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token
    }

    with open(constants.YOUTUBE_AUTH_PICKLE, "wb") as creds:
        pickle.dump(credentials, creds)

    with open(constants.YOUTUBE_SECRETS, "w") as secrets:
        json.dump(youtube_tokens, secrets)

def set_up_spotify_token():
    if not os.path.isfile(constants.SPOTIFY_CLIENT_SECRETS):
        return

    with open(constants.SPOTIFY_CLIENT_SECRETS) as f:
        spotify_client_tokens = json.load(f)

    scope = "playlist-modify-public"

    sp_oauth = oauth2.SpotifyOAuth(
        client_id=spotify_client_tokens["client_id"],
        client_secret=spotify_client_tokens["client_secret"],
        redirect_uri=spotify_client_tokens["redirect_uri"],
        scope=scope
    )

    sp_oauth.show_dialog = True

    auth_url = sp_oauth.get_authorize_url()
    print("Please go to this URL: {}".format(auth_url))
    response = input("Paste the above link into your browser, " \
    "then paste the redirect url here: ")

    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code, check_cache=False)

    spotify_tokens = {
        "access_token": token_info["access_token"],
        "refresh_token": token_info["refresh_token"]
    }

    with open(constants.SPOTIFY_AUTH_PICKLE, "wb") as creds:
        pickle.dump(sp_oauth, creds)

    with open(constants.SPOTIFY_SECRETS, "w") as secrets:
        json.dump(spotify_tokens, secrets)

if __name__ == "__main__":
    main()