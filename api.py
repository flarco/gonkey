import yaml, os

from gmusicapi import Mobileclient

DIR = os.path.dirname(os.path.realpath(__file__))

# Get credentials
with open(DIR + '/creds.yml') as creds_file:
  cred = yaml.load(creds_file)


api = Mobileclient()
logged_in = api.login(
  cred['google_email'],
  cred['google_password'],
  Mobileclient.FROM_MAC_ADDRESS
)

print(logged_in)