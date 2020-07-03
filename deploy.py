"""Deployment script

This script deploys the app to AWS Lambda.

Below are the steps for this deployment script:
1. Set the Youtube parameters in AWS SSM Parameter Store
2. Set the Spotify parameters in AWS SSM Parameter Store
3. Create a S3 bucket to store the AWS Lambda app configuration
4. If the user specifies the "--layer" argument in the command line, the script
   will build the helper layer zip
5. Use the SAM cli to package and deploy to AWS Lambda

"""

import os, json, argparse, shutil
from distutils.dir_util import copy_tree

import boto3

import src.constants as constants

parser = argparse.ArgumentParser(
    description='Deploy Youtube to Spotify Playlist to AWS Lambda.'
)
parser.add_argument(
    '--layer',
    action="store_true",
    default=False,
    help='Build the helper layer zip (default: %(default)s)'
)

args = parser.parse_args()

ssm_client = boto3.client('ssm')

def write_parameter(prefix, key, value):
    """
        Writes the provided parameter to AWS SSM Parameter Store.
    """

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
    """
        Writes the local Youtube parameters to AWS SSM Parameter Store.
    """

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
    """
        Writes the local Spotify parameters to AWS SSM Parameter Store.
    """

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
    """
        Creates the S3 bucket to store the AWS Lambda app configuration (if needed)
    """

    print("[NOTICE] Creating S3 bucket.")
    s3_client = boto3.client('s3')

    bucket_name = "youtube-to-spotify"

    s3_client.create_bucket(
        Bucket=bucket_name
    )

def build_layer():
    """
        Builds the helper layer zip.

        This adheres to the AWS Lambda layer requirement of the zip being structured
        as follows:
        "python/lib/python3.x/site-packages/..."
    """

    print("[NOTICE] Building helper layer.")
    src = "YoutubeToSpotifyEnv/lib/python3.7/site-packages"
    dest = "layers/youtube-to-spotify-helper-layer/python/lib/python3.7/site-packages/"

    try:
        # Create the directory to adhere to AWS Lambda layer structure requirement
        os.makedirs(src)
    except:
        # The directory may already exist
        pass

    # Copy virtual env packages to directory
    copy_tree(src, dest)

    # Create the zip
    shutil.make_archive(
        "layers/youtube-to-spotify-helper-layer/function",
        'zip',
        "layers/youtube-to-spotify-helper-layer/",
        "python"
    )

def deploy_lambda():
    """
        Uses the SAM cli to package and deploy to AWS Lambda
    """
    print("[NOTICE] Deploy Lambda function.")   
    os.system("sam package --template-file template.yaml --s3-bucket youtube-to-spotify --s3-prefix lambda-templates/youtube-to-spotify --output-template-file packaged.yaml")
    os.system("sam deploy --template-file packaged.yaml --stack-name YoutubeToSpotify --s3-bucket youtube-to-spotify --capabilities 'CAPABILITY_IAM'")

def main():
    set_up_youtube_secrets()
    set_up_spotify_secrets()
    create_s3_bucket()
    
    if args.layer:
        # If the user specifies the "--layer" argument, build the helper layer
        build_layer()

    deploy_lambda()

if __name__ == "__main__":
    main()

