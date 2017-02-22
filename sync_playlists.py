import sys

from google_music import GMusic
from media_monkey import MM
from helpers import settings, log

log('Start!')

log('Loading MM.')
mm = MM(settings)

log('Loading GM.')
gmusic = GMusic(settings, mm)

log('Syncing playlists!')
gmusic.sync_all_playlists(only_metadata = True)

log('End!')