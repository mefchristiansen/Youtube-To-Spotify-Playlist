import os, json, argparse, shutil
from distutils.dir_util import copy_tree

import boto3

import src.constants as constants

parser = argparse.ArgumentParser(description='Deploy Youtube to Spotify Playlist to AWS Lambda.')
parser.add_argument(
    '--layer',
    action="store_true",
    default=False,
    help='Rebuild the helper layer zip (default: %(default)s)'
)

args = parser.parse_args()

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
    print("[NOTICE] Setting Youtube secrets.")
    if not os.path.isfile(constants.YOUTUBE_SECRETS):
        print(
            "[ERROR] The Youtube secrets file does exist. " \
            "Please run the set up script (set_up.py) first."
        )
        return

    with open(constants.YOUTUBE_SECRETS) as f:
        youtube_secrets = json.load(f)

    for key, value in youtube_secrets.items():
        write_parameter("Youtube", key, value)

def set_up_spotify_secrets():
    print("[NOTICE] Setting Spotify secrets.")
    if not os.path.isfile(constants.SPOTIFY_SECRETS):
        print(
            "[ERROR] The Spotify secrets file does exist. " \
            "Please run the set up script (set_up.py) first."
        )
        return

    with open(constants.SPOTIFY_SECRETS) as f:
        spotify_secrets = json.load(f)

    for key, value in spotify_secrets.items():
        write_parameter("Spotify", key, value)

def create_s3_bucket():
    print("[NOTICE] Creating S3 bucket.")
    s3_client = boto3.client('s3')

    bucket_name = "youtube-to-spotify"

    s3_client.create_bucket(
        Bucket=bucket_name
    )

def rebuild_layer():
    print("[NOTICE] Rebuilding helper layer.")
    src = "YoutubeToSpotifyEnv/lib/python3.7/site-packages"
    dest = "layers/youtube-to-spotify-helper-layer/python/lib/python3.7/site-packages/"

    try:
        os.makedirs(src)
    except:
        pass

    copy_tree(src, dest)

    shutil.make_archive("layers/youtube-to-spotify-helper-layer/function", 'zip', dest)

def deploy_lambda():
    print("[NOTICE] Deploy Lambda function.")   
    os.system("sam package --template-file template.yaml --s3-bucket youtube-to-spotify --s3-prefix lambda-templates/youtube-to-spotify --output-template-file packaged.yaml")
    os.system("sam deploy --template-file packaged.yaml --stack-name YoutubeToSpotify --s3-bucket youtube-to-spotify --capabilities 'CAPABILITY_IAM'")

def main():
    set_up_youtube_secrets()
    set_up_spotify_secrets()
    create_s3_bucket()
    
    if args.layer:
        rebuild_layer()

    deploy_lambda()

if __name__ == "__main__":
    main()

