from gmusicapi import Mobileclient
import yaml



# Get credentials

api = Mobileclient()
api.login('user@gmail.com', 'my-password', Mobileclient.FROM_MAC_ADDRESS)