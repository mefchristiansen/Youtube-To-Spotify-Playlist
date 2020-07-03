import os, json

import boto3
import constants

from ssm_parameter_store import SSMParameterStore

class ParameterStore(object):
    def __init__(self, prefix, secrets_file):
        self._prefix = prefix
        self._ssm_client = boto3.client('ssm')
        self._ssm_parameter_store = SSMParameterStore(prefix=f'/YoutubeToSpotify/Prod/{self._prefix}')
        self._secrets_file = secrets_file

    def get_secrets(self):
        env = os.environ.get('ENV')

        if env == "production":
            return self._ssm_parameter_store
        elif env == "development":
            if not os.path.isfile(self._secrets_file):
                print(
                    f"[ERROR] The {self._prefix} secrets file does exist. " \
                    "Please run the set up script (set_up.py) first."
                )
                return

            with open(self._secrets_file) as secrets_file:
                return json.load(secrets_file)
        else:
            print("[ERROR] Invalid environment.")
            return

    def update_secrets(self, updated_secrets):
        env = os.environ.get('ENV')

        if env == "production":
            for key, value in updated_secrets.items():
                self.write_parameter(key, value)

            self._ssm_parameter_store.refresh()

        elif env == "development":
            secrets = self.get_secrets()

            for key, value in updated_secrets.items():
                secrets[key] = value

            with open(self._secrets_file, 'w') as f:
                json.dump(secrets, f)
        else:
            print("[ERROR] Invalid environment.")
            return

    def write_parameter(self, key, value):
        try:
            self._ssm_client.put_parameter(
                Name=f'/YoutubeToSpotify/Prod/{self._prefix}/{key}',
                Value=value,
                Type='SecureString',
                Overwrite=True
            )
        except:
            print(f"[ERROR] Error setting parameter ({self._prefix}/{key}).")
            return