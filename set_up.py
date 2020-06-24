import json

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    youtube_tokens = set_up_youtube_tokens()

    with open('secrets.json', 'w') as f:
        json.dump(youtube_tokens, f)

    return

def set_up_youtube_tokens():
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    auth_url, _ = flow.authorization_url(prompt='consent')
    print('Please go to this URL: {}'.format(auth_url))
    code = input('Enter the authorization code: ')
    obtained_tokens = flow.fetch_token(code=code)
    credentials = flow.credentials

    return {
        "youtube": {
            "access_token": obtained_tokens['access_token'],
            "refresh_token": obtained_tokens['refresh_token'],
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret
        }
    }

if __name__ == "__main__":
    main()