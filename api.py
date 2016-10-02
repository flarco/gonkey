import sys

from google_music import GMusic
from media_monkey import MM

from helpers import (
  settings,
  dict2,
)


gmusic = GMusic(settings)
gmusic.load_data()
# gmusic.update_playlist('Coldplay')

sys.exit()

mm = MM(settings)
mm.load_tables()
mm.load_data()
print('Done')