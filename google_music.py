
from collections import namedtuple, OrderedDict

from gmusicapi import Mobileclient, Musicmanager

from helpers import (
  settings,
  dict2,
  log,
)


'playCount'
tracks_pk_keys = [
  'albumArtist',
  'album',
  'artist',
  'title',
]
get_song_pk = lambda track: '-'.join(track[k] for k in tracks_pk_keys)

class GMusic:

  tables_api_call = [
    ('songs','get_all_songs'),
    # ('playlists','get_all_playlists'),
    ('playlists','get_all_user_playlist_contents'),
    ('genres','get_genres'),
  ]
  tables_data = dict2()
  all_songs = {}

  mm = None


  def __init__(self, settings, mm=None):
    self.mm = mm
    self.api = Mobileclient()
    self.oauth_path = settings['oauth_file_name']
    self.chosen_playlists = settings['media_monkey_playlists']
    self.gm_manager = Musicmanager()
    self.gm_manager.login(oauth_credentials=self.oauth_path)

    logged_in = self.api.login(
      settings['google_email'],
      settings['google_password'],
      Mobileclient.FROM_MAC_ADDRESS
    )
    log('Logged In: {}'.format(logged_in))
  
  def load_data(self, only_tables=[]):
    "Loads GMusic Metadata into memory"
    for table_api_call in self.tables_api_call:
      table_name, api_call = table_api_call
      if not only_tables or table_name in only_tables:
        self.tables_data[table_name] = {r['id']:dict2(r) for r in getattr(self.api, api_call)()}
        log("{} -> {}".format(table_name, len(self.tables_data[table_name])))
  
  def compare_playlist(self, mm_playlist, gm_playlist):
    "Compare a gmusic playlist vs a MM playlist"
    "return True for equal, False for not equal"

    if not self.mm:
      log('MediaMonkey library not loaded')
      return
  
  def delete_playlist(self, playlist_name):
    "Delete Playlist from GM"
    pl_id = self.playlist_names[playlist_name].id
    succ = self.api.delete_playlist(pl_id)
    if succ: log(playlist_name + ' deleted!')
    else: log(playlist_name + ' FAILED to delete!')
    
  def add_track(self, mm_track):
    "Add MM song to GM"
    song_path = mm_track.SongPath
    song_path = "D" + song_path if song_path.startswith(":") else song_path
    (uploaded, matched, not_uploaded) = self.gm_manager.upload([song_path])

    song_id = None
    if song_path in not_uploaded:
      log(song_path + ' not uploaded! -> ' + not_uploaded[song_path])
      if 'ALREADY_EXISTS' in not_uploaded[song_path]:
        song_id = not_uploaded[song_path].split('ALREADY_EXISTS(')[-1][:-1]
    else:
      song_id = uploaded[song_path]

    return song_id

  def update_song_metadata(self, gm_track_id, mm_track):
    "Update Song Rating and Play Count"
    gm_song = self.tables_data.songs[gm_track_id]
    gm_rating = gm_song['rating']
    mm_rating = str(int(float(mm_track.Rating)/20))
    
    if mm_rating != gm_rating:
      gm_song = mm_rating
      self.api.change_song_metadata(gm_song)
    
    play_count_delta = mm_track.PlayCounter - gm_song.playCount
    if play_count_delta > 0:
      self.api.increment_song_playcount(gm_track_id, play_count_delta)

  def add_all_playlists(self):
    "Add all chosen playlists specified in settings file"
    for playlist in self.chosen_playlists:
      self.add_playlist(playlist)
    
  def add_playlist(self, playlist_name):
    "Add MM playlist to GM"

    if not self.mm:
      log('MediaMonkey library not loaded')
      return
    
    all_playlists = dict2({p.name:p for p_id, p in self.tables_data.playlists.items()})
    if playlist_name in all_playlists:
      log(playlist_name + ' found! Deleting...')
      self.api.delete_playlist(all_playlists[playlist_name].id)

    pl_id = self.api.create_playlist(playlist_name)
    if pl_id: log(playlist_name + ' created!')
    else: log(playlist_name + ' FAILED to create!')

    mm_playlist = self.mm.playlist_songs[playlist_name]

    track_ids = []
    for track_pk, mm_track in mm_playlist.items():
      # check if song exists in GMusic
      if track_pk in self.all_songs:
        gm_track_id = self.all_songs[track_pk].id
      else:
        gm_track_id = self.add_track(mm_track)
      
      track_ids.append(gm_track_id)
      
    song_ids_added = self.api.add_songs_to_playlist(playlist_id=pl_id, song_ids=track_ids)
    
    log('{} songs added to playlist{}!'.format(len(song_ids_added),playlist_name))


  def arrange_data(self):
    "Arrnange various lists with proper key identification"
    self.all_songs = {get_song_pk(track): track  for id, track in self.tables_data.songs.items()}
    self.playlist_names = {p_rec.name: p_rec  for id, p_rec in self.tables_data.playlists.items()}
    self.playlist_songs = {p_rec.name: OrderedDict()  for id, p_rec in self.tables_data.playlists.items()}
    
    for pl_id, playlist in self.tables_data.playlists.items():
      for track in playlist.tracks:
        pl_name = playlist.name
        pl_song = self.tables_data.songs[track['trackId']]
        song_pk = get_song_pk(pl_song)
        self.playlist_songs[pl_name][song_pk] = pl_song



  def update_playlist(self, playlist_name):
    "Updates the GMusic Playlist from MM"

    

    # Arrange data in keys
    all_playlists = dict2({p.name:p for p in self.tables_data.playlists})
    for name, meta in all_playlists.items():
      all_playlists[name].tracks_ = OrderedDict({track['id']: dict2(track) for track in all_playlists[name].tracks})
    

    # Check if playlist exists
    if playlist_name in all_playlists:
      log(playlist_name + ' found!')
      delete_playlist(playlist_name)
      
    add_playlist(playlist_name)
      
if __name__ == '__main__':
  from media_monkey import MM
  mm = MM(settings)
  mm.load_tables()
  mm.load_data()
  mm.arrange_data()

  gmusic = GMusic(settings, mm)
  gmusic.load_data()
  gmusic.arrange_data()
  # gmusic.add_playlist('a_CoralieClement')
  gmusic.add_all_playlists()
  print(list(gmusic.playlist_songs['Coldplay'].keys())[0])