"""Constants

Program constants

"""

import os
from pathlib import Path

file_path = Path(__file__).parent.absolute()

YOUTUBE_CLIENT_SECRETS = file_path / Path("secrets/client-secrets/youtube_client_secrets.json")
SPOTIFY_CLIENT_SECRETS = file_path / Path("secrets/client-secrets/spotify_client_secrets.json")

YOUTUBE_SECRETS = file_path / Path("secrets/secrets/youtube_secrets.json")
SPOTIFY_SECRETS = file_path / Path("secrets/secrets/spotify_secrets.json")