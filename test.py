import os

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

def main():
    if os.getenv('ENV') == "development":
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()

    print(credentials)

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        myRating="like"
    )

    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()