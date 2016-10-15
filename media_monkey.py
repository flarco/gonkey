from collections import namedtuple, OrderedDict
from helpers import (
  dict2,
  log,
  settings
)

from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.engine import reflection
from sqlalchemy.schema import CreateTable

class MM:
  "Class represnting MediaMonkey library"

  table_list_key = {
    'songs' : 'ID',
    'genres' : 'GenreName',
    'playlists' : 'PlaylistName',
    'playlistsongs' : 'IDPlaylistSong',
  }

  tables_meta = dict2()
  tables_data = dict2()
  playlist_songs = {}


  def __init__(self, settings, load=True):
    "Create sqlalchemy engine"
    self.engine = create_engine('sqlite:///' + settings['media_monkey_db_path'])

    if load:
      self.load_tables()
      self.load_data()
      self.arrange_data()


  def load_tables(self):
    "Loads table/columns objects from SQLite database"
    
    insp = reflection.Inspector.from_engine(self.engine)  # http://docs.sqlalchemy.org/en/latest/core/reflection.html
    meta = MetaData()

    for table_name in self.table_list_key:
      self.tables_meta[table_name] = Table(table_name, meta)
      insp.reflecttable(self.tables_meta[table_name], None)
    

  def load_data(self):
    "Load data into memory from Database"

    for table_name, key in self.table_list_key.items():
      q_select = self.tables_meta[table_name].select()
      result = self.engine.execute(q_select)
      Record = namedtuple(table_name, result.keys())
      # self.tables_data[table_name] = [Record(*row) for row in result]
      self.tables_data[table_name] = {r[key]:dict2(r) for r in result}
      log("{} -> {}".format(table_name, len(self.tables_data[table_name])))


  def arrange_data(self):
    "Arrange various lists' data with proper key identification"
    tracks_pk_keys = [
      'AlbumArtist',
      'Album',
      # 'Artist',
      'SongTitle',
    ]

    def get_song_pk(song):
      # if song['AlbumArtist'] == '' or (song['Artist'] != '' and song['AlbumArtist'] != ''):
      if song['AlbumArtist'] == '':
        song['AlbumArtist'] = song['Artist']
      
      return '-'.join(song[k] for k in tracks_pk_keys)

    self.all_songs = {get_song_pk(track): track  for id, track in self.tables_data.songs.items()}
    playlist_id = {p_rec.IDPlaylist: p_rec  for playlist, p_rec in self.tables_data.playlists.items()}
    self.playlist_songs = {playlist: OrderedDict()  for playlist in self.tables_data.playlists}
    
    for id, pl_song in self.tables_data.playlistsongs.items():
      pl_name = playlist_id[pl_song.IDPlaylist].PlaylistName
      song = self.tables_data.songs[pl_song.IDSong]
      song_pk = get_song_pk(song)
      self.playlist_songs[pl_name][song_pk] = song


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
    
    
  def increment_song_playcount(self, track, play_count_delta):
    "Increment a song playcount by :play_count_delta, send UPDATE query to SQLite DB"
    song_table = self.tables_meta['songs']
    new_playcount = track.PlayCounter + play_count_delta
    q_update = song_table.update().where(song_table.c.ID==track.ID).values(PlayCounter = new_playcount)
    result = self.engine.execute(q_update)
    if result:
      return True
    else:
      return False


