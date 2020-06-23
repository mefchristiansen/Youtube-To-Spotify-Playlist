import os

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=Loader)

import boto3

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

def main():
    return

    API_KEY="AIzaSyDgwhC2BJI1tIw1mBwHUBeZNcHFNZ16BRY"
    channel_id = "UCbXgNpp0jedKWcQiULLbDTA"
    url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={API_KEY}'

    # url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}'

def init_youtube_client():

    if os.getenv('ENV') == "development":
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)

    auth_url, _ = flow.authorization_url(prompt='consent')
    print('Please go to this URL: {}'.format(auth_url))
    code = 
    flow.fetch_token(code=code)

    credentials = flow.credentials

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        myRating="like"
    )

    response = request.execute()

    print("HELLO")

    print(response)

def refresh():
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)




    
