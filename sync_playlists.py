import sys

from google_music import GMusic
from media_monkey import MM
from helpers import settings

mm = MM(settings)
gmusic = GMusic(settings, mm)
gmusic.add_all_playlists()