import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=Loader)

import boto3


def main():
	return

if __name__ == "__main__":
	main()