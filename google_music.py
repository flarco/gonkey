from collections import namedtuple, OrderedDict

from gmusicapi import Mobileclient, Musicmanager, Webclient

from mutagen import File

from helpers import (
  settings,
  dict2,
  log,
  DIR,
)


tracks_pk_keys = [
  'albumArtist',
  'album',
  'title',
]
tracks_pk2_keys = [
  'artist',
  'album',
  'title',
]

def get_song_pk(track):
  if not 'albumArtist' in track or track['albumArtist'] == '': track['albumArtist'] = track['artist']
  return '-'.join(track[k] for k in tracks_pk_keys)
def get_song_pk2(track):
  return '-'.join(track[k] for k in tracks_pk2_keys)


class GMusic:
  "Class representing the library from user's google music profile"

  tables_api_call = [
    ('songs','get_all_songs'),
    # ('playlists','get_all_playlists'),
    ('playlists','get_all_user_playlist_contents'),
    ('genres','get_genres'),
  ]
  tables_data = dict2()
  all_songs = {}

  mm = None


  def __init__(self, settings, mm=None, load=True):
    self.mm = mm
    self.api = Mobileclient()
    self.web_client = Webclient()
    self.oauth_path = DIR + '/'+ settings['oauth_file_name']
    self.chosen_playlists = settings['media_monkey_playlists']
    self.gm_manager = Musicmanager()
    self.gm_manager.login(oauth_credentials=self.oauth_path)

    logged_in = self.api.login(
      settings['google_email'],
      settings['google_password'],
      Mobileclient.FROM_MAC_ADDRESS
    )
    log('Logged In Mobileclient: {}'.format(logged_in))

    # web_client does not work...
    '''
    logged_in = self.web_client.login(
      settings['google_email'],
      settings['google_password']
    )
    log('Logged In Webclient: {}'.format(logged_in))
    '''

    if load:
      self.load_data()
      self.arrange_data()
  

  def load_data(self, only_tables=[]):
    "Loads GMusic Metadata into memory"
    for table_api_call in self.tables_api_call:
      table_name, api_call = table_api_call
      if not only_tables or table_name in only_tables:
        self.tables_data[table_name] = {r['id']:dict2(r) for r in getattr(self.api, api_call)()}
        log("{} -> {}".format(table_name, len(self.tables_data[table_name])))
  
  def sync_playlist(self, playlist, only_metadata = False):
    "Synchronize the playlist between MM and GM: List of songs, ratings, play count"

    if not playlist in self.mm.playlist_songs:
      log('Playlist {} missing in MediaMonkey'.format(playlist))
      return

    if not playlist in self.playlist_songs:
      log('Playlist {} missing in Google Music'.format(playlist))
      self.add_playlist(playlist)
      return
    
    mm_playlist = self.mm.playlist_songs[playlist]
    gm_playlist = self.playlist_songs[playlist]
    
    if not only_metadata:
      if not self.compare_playlist(mm_playlist, gm_playlist):
        self.add_playlist(playlist)
        self.playlist_modified.append(playlist)
      
    gm_playlist = self.playlist_songs[playlist]
    for track_name in mm_playlist:
      if not track_name in gm_playlist:
        log('{} not found in gm_playlist "{}"...'.format(track_name, playlist))
        continue
      
      self.update_song_metadata(
        gm_track_id = gm_playlist[track_name].id,
        mm_track = mm_playlist[track_name]
      )
    
    log('Synced {}!'.format(playlist))
    

  def compare_playlist(self, mm_playlist, gm_playlist):
    """Compare a gmusic playlist vs a MM playlist
    return True for equal, False for not equal"""

    equal = True

    if not self.mm:
      log('MediaMonkey library not loaded')
      return None
    
    mm_playlist_list = tuple([t for t in mm_playlist])
    gm_playlist_list = tuple([t for t in gm_playlist])

    if len(mm_playlist) != len(gm_playlist):
      equal = False
    else:
      if mm_playlist_list != gm_playlist_list:
        equal = False
    
    if not equal:
      log('MM list != GM list')
      # log('{} != {}'.format(str(mm_playlist_list), str(gm_playlist_list)))
      gm_set = set(gm_playlist_list)
      for t in mm_playlist_list:
        if not t in gm_set:
          log('Track {} missing in GM'.format(t))
    
    return equal


  def delete_playlist(self, playlist_name):
    "Delete Playlist from GM"
    pl_id = self.playlist_names[playlist_name].id
    succ = self.api.delete_playlist(pl_id)
    if succ: log(playlist_name + ' deleted!')
    else: log(playlist_name + ' FAILED to delete!')


  def add_track(self, mm_track):
    "Add MM song to GM"
    song_path = mm_track.SongPath
    
    if song_path.startswith(":"):
      drive_prefix = 'Y' if 'DATA_3TB_BACKUP' in song_path else 'D'
      song_path = drive_prefix + song_path
    
    (uploaded, matched, not_uploaded) = self.gm_manager.upload([song_path])

    song_id = None
    if song_path in not_uploaded:
      log(song_path + ' not uploaded! -> ' + not_uploaded[song_path])
      if 'ALREADY_EXISTS' in not_uploaded[song_path]:
        song_id = not_uploaded[song_path].split('ALREADY_EXISTS(')[-1][:-1]
    else:
      song_id = uploaded[song_path]

      # To be improved for album art update
      '''
      artwork = File(song_path).tags['APIC:'].data # access APIC frame and grab the image
      with open('artwork.jpg', 'wb') as img:
        img.write(artwork) # write artwork to new image
      self.web_client.upload_album_art(song_id, 'artwork.jpg')
      '''

    return song_id


  def update_song_metadata(self, gm_track_id, mm_track):
    "Update Song Rating and Play Count"
    gm_song = self.tables_data.songs[gm_track_id]
    gm_song['rating'] = 0 if not 'rating' in gm_song else gm_song['rating']
    gm_song['playCount'] = 0 if not 'playCount' in gm_song else gm_song['playCount']
    mm_rating = str(int(float(mm_track.Rating)/20))
    song_name = mm_track.AlbumArtist.encode('utf8') + b' -- ' + mm_track.SongTitle.encode('utf8')
    
    if mm_rating != gm_song['rating']:
      gm_song['rating'] = mm_rating
      log('Updating GM rating for {}.'.format(song_name))
      self.api.change_song_metadata(gm_song)
    
    play_count_delta = mm_track.PlayCounter - gm_song.playCount
    if play_count_delta > 0:
      log('Updating GM playcount for {}. Incrementing by {} to {}.'.format(song_name, play_count_delta, mm_track.PlayCounter))
      self.api.increment_song_playcount(gm_track_id, play_count_delta)
    elif play_count_delta < 0:
      log('Updating MM playcount for {}. Incrementing by {} to {}.'.format(song_name, -1 * play_count_delta, gm_song.playCount))
      self.mm.increment_song_playcount(mm_track, -1 * play_count_delta)


  def add_all_playlists(self):
    "Add all chosen playlists specified in settings file"
    for playlist in self.chosen_playlists:
      self.add_playlist(playlist)

  def sync_all_playlists(self, only_metadata = False):
    "Compare all chosen playlists specified in settings file, adjust as necessary"
    self.playlist_modified = []
    
    for playlist in self.chosen_playlists:
      self.sync_playlist(playlist, only_metadata)
    
    # if self.playlist_modified:
    #   self.added_songs = False
    #   log('Reloading to count newly added songs.')
    #   self.load_data()
    #   self.arrange_data()
    #   self.sync_playlist
    #   for playlist in self.playlist_modified:
    #     self.sync_playlist(playlist)
    

  def add_playlist(self, playlist_name):
    "Add MM playlist to GM"

    if not self.mm:
      log('MediaMonkey library not loaded')
      return
    
    gm_all_playlists = dict2({p.name:p for p_id, p in self.tables_data.playlists.items()})

    mm_playlist = self.mm.playlist_songs[playlist_name]

    track_ids = []
    for track_pk, mm_track in mm_playlist.items():
      # check if song exists in GMusic
      gm_track_id = None
      if track_pk in self.all_songs:
        gm_track_id = self.all_songs[track_pk].id
      else:
        log('"{}" not found! Adding...'.format(track_pk))
        gm_track_id = self.add_track(mm_track)
      
      if gm_track_id:
        track_ids.append(gm_track_id)
      
    if playlist_name in gm_all_playlists:
      log(playlist_name + ' found! Deleting entries...')
      # self.api.delete_playlist(gm_all_playlists[playlist_name].id)
      entry_ids = [track['id'] for track in gm_all_playlists[playlist_name].tracks]
      self.api.remove_entries_from_playlist(entry_ids)
      pl_id = gm_all_playlists[playlist_name].id
    else:
      pl_id = self.api.create_playlist(playlist_name)
      if pl_id: log(playlist_name + ' created!')
      else: log(playlist_name + ' FAILED to create!')
    
    if True or len(track_ids) <= len(mm_playlist.keys()):
      song_ids_added = self.api.add_songs_to_playlist(playlist_id=pl_id, song_ids=track_ids)
  
      log('{} songs added to playlist {}!'.format(len(song_ids_added),playlist_name))
      
      # log('Reloading playlists')
      # self.load_data(only_tables=['playlists'])
      # self.arrange_data()
    else:
      log('Aborded adding playlist {}! Number of Songs mismatch {} != {}'.format(playlist_name), len(track_ids), len(mm_playlist.keys()))
        
      
  def arrange_data(self):
    "Arrange various lists' data with proper key identification"
    
    self.all_songs = {}
    for id, track in self.tables_data.songs.items():
      self.all_songs[get_song_pk(track)] = track
      self.all_songs[get_song_pk2(track)] = track
    
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
      # self.delete_playlist(playlist_name)
      
    self.add_playlist(playlist_name)
  
  
  def search_songs(self, search_str):
    "Search all songs in library for a query"
    results = []
    for pk_song in self.all_songs:
      if search_str.lower() in pk_song.lower():
        results.append(pk_song)
    
    if len(results) > 0:
      print("Found {} songs!".format(len(results)))
      for pk_song in results:
        print(pk_song)