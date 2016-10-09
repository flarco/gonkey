# gonkey
MediaMonkey with Google Music!

MediaMonkey = MM

GoogleMusic = GM

## Operations to be implemented:
  - ~~Update song rating~~
  - ~~Update song play count~~
  - ~~Update playlist~~
  - Upload/update album art for song (<https://github.com/simon-weber/gmusicapi/issues/242>)
  - Handle unicode strings
  - Two-way synchronization (GM -> MM):
    - Metadata (rating, play count)
    - Playlist order
  
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
Put in your credentials, the MM database path and the name of the playlists you want to be synced. Make sure to follow the YAML conventions.

### Generate OAuth file
In order to upload songs, we need to be authenticated.
Make sure to have the variable `oauth_file_name` defined in the `settings.yml`, or leave it as it is.

Then run:
```
python generate_oauth_file.py
```

It should open the browser and ask you to authenticate.
Once done, the file will be created, and you'll be ready to upload songs.

## Sync Playlists
This is the most sought-after capability. This will synchronize the chosen playlist songs from MediaMonkey (MM) and Google Music (GM).
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

