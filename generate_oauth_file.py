from helpers import DIR, settings
from gmusicapi import Musicmanager

mmanager = Musicmanager()
mmanager.login(oauth_credentials=DIR + '/'+ settings['oauth_file_name'])