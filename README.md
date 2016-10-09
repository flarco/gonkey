# gonkey
MediaMonkey with Google Music


## Operations to be implemented:
 - Update song rating (api.change_song_metadata)
 - Update song play count (api.increment_song_playcount)
 - Update playlist
   - Create (api.create_playlist)
   - Edit (api.edit_playlist)
   - Delete (api.delete_playlist)

## Setup
Assuming you have `git`, `python` & `pip` installed, you need to install the dependencies.

First, clone this repo:
```
git clone https://github.com/flarco/gonkey.git
cd gonkey
```
Then install pip requirements:
```
pip install -r requirements.pip
```

### Create settings.yml
See the template `settings.template.yml`. Create a new file called `settings.yml` in the root folder.
Put it your credentials, the MM database path and the name of the playlists you want to be synced. Make sure to follow the YAML conventions.

## Sync Playlists
This is the most sought-after capability. This will synchronize the chosen playlist songs from MediaMonkey (GM) and Google Music (GM).
So far this is a one-way synchronization (MM to GM) -- Two way to be implemented in the future.

To perform synchronization, make sure the 'media_monkey_playlists' variable is updated with the list of playlists you want synced.
Then run:

```
python sync_playlists.py
```

It should automatically:
 - Re/Create the playlist with correct songs
 - Upload missing songs in GM library
 - Update each song's rating and play count (matching MM)

