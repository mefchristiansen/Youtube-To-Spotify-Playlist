import os, json

import boto3

import constants

ssm_client = boto3.client('ssm')

def write_parameter(prefix, key, value):
    try:
        ssm_client.put_parameter(
            Name=f'/YoutubeToSpotify/Prod/{prefix}/{key}',
            Value=value,
            Type='SecureString',
            Overwrite=True
        )
    except:
        print(f"[ERROR] Error setting parameter ({prefix}/{key}).")
        return

def set_up_youtube_secrets():
    if not os.path.isfile(constants.YOUTUBE_SECRETS):
        return

    with open(constants.YOUTUBE_SECRETS) as f:
        youtube_secrets = json.load(f)

    for key, value in youtube_secrets.items():
        write_parameter("Youtube", key, value)

def set_up_spotify_secrets():
    if not os.path.isfile(constants.SPOTIFY_SECRETS):
        return

    with open(constants.SPOTIFY_SECRETS) as f:
        spotify_secrets = json.load(f)

    for key, value in spotify_secrets.items():
        write_parameter("Spotify", key, value)

def create_s3_bucket():
    s3_client = boto3.client('s3')

    bucket_name = "youtube-to-spotify"

    s3_client.create_bucket(
        Bucket=bucket_name
    )

def deploy_lambda():    
    return

def deploy():
    set_up_youtube_secrets()
    set_up_spotify_secrets()
    create_s3_bucket()
    deploy_lambda()