# Youtube to Spotify Playlist

<br>

A Python script that converts your Youtube liked videos into a Spotify playlist.

This script is deployable to AWS Lambda where it will execute on a scheduled basis so that the Spotify playlist stays up to date as new videos are liked on Youtube.

## Local Set Up

This is written in Python 3.7 and requires a virtual environment titled `YoutubeToSpotifyEnv`

### 1. Install Dependencies

`pip3 install -r requirements.txt`

### 2. Youtube Authentication

To set up Youtube authentication, follow the guide here: https://developers.google.com/youtube/v3/getting-started/

Essentially what you want to do is to created a Desktop app OAuth 2.0 Client ID and download the client secret JSON file.

You are going to want to save this file into the folder `src/secrets/client_secrets/` as `youtube_client_secrets.json`. Remember to set `redirect_uris` to `urn:ietf:wg:oauth:2.0:oob`. See the template Youtube client secrets JSON file in the secrets folder as an example.

**Remeber to not commit this file to Git**

### 3. Spotify Authentication

To set up Spotify authentication, follow the guide here:
https://developer.spotify.com/documentation/general/guides/app-settings/

Essentially what you want to do is to create a new app, whitelist the URI `http://localhost`, and save the client_id, client_secret and the redirect_uri (which will be `http://localhost`) into the folder `src/secrets/client_secrets/` as `spotify_client_secrets.json`. See the template Spotify client secrets JSON file in the secrets folder as an example.

**Remeber to not commit this file to Git**

### 4. Set Up Script

After having gotten the Youtube and Spotify credentials, run the setup script `setup.py` and follow the instructions in the terminal to set up both the Youtube and Spotify clients.

## Run

To run the script locally, run the script `src/youtube_to_spotify.py`. This will populate a new Spotify playlist (titled "Youtube Liked Songs") with your Youtube liked songs. You will need to run the set up script (as stated above) before you run this script.

## Deploy

Before deploying to AWS Lambda, I recommend you run the `src/youtube_to_spotify.py` script locally first. Due to the maximum execution time of 15 minutes, if you have above 1000 liked videos on Youtube, the script will not be able to process all the liked videos. If you run the script locally first and then deploy to AWS, the already processed videos will be recorded and the Lambda function will only process newly liked videos.

### AWS Role

In order to run, the Lambda function requires basic permissions.

Create a new role titled: "YoutubeToSpotify", with the following policies:
- AWSLambdaExecute
- AWSLambdaBasicExecutionRole
- A custom policy to enabled access and edit permissions to AWS SSM Paramter Store with the following structure:

```json

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ssm:PutParameter",
                "ssm:GetParameter"
            ],
            "Resource": "arn:aws:ssm:us-east-1:079866621733:parameter/YoutubeToSpotify/*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "ssm:DescribeParameters",
            "Resource": "*"
        }
    ]
}

```

### Deployment Script

To deploy the function to AWS Lambda, run the deployment script `deploy.py` and follow the instructions.

The deployment script will build the helper layer needed by this function if the `---layer` flag is include. Run `python deploy.py --help` for more details. You will need to build this helper layer on the first deployment, and if you make any changes to the functions packages.

The deployment script will:
- Set the Youtube parameters in AWS SSM Parameter Store
- Set the Spotify parameters in AWS SSM Parameter Store
- Create a S3 bucket to store the AWS Lambda app configuration
- Build the helper layer zip
- Use the SAM cli to package and deploy to AWS Lambda

After the script successfully executes, the Lambda function will run on a scheduled interval (1 hour by default) and add your newly liked Youtube video to the Spotify playlist.

## Limitations

This project uses [Youtube DL](https://github.com/ytdl-org/youtube-dl) to extract a video's information to determine if it is a song or not, and Spotify's Web API to see if the corresponding track exists on Spotify. Be aware that the results are not always perfect, as videos that are songs may be missed, the incorrect title or artist may parsed from the video, the song may not exist on Spotify, or the Spotify API may match the video with the wrong track.