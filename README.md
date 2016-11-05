![coollogo_com-7561364](https://cloud.githubusercontent.com/assets/7671010/19522237/689d2144-95e4-11e6-83e2-b430e7394f1d.png)

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
    - Rating
    - ~~Play count~~
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

 This is an example output:
 ```
 C:\gonkey> python .\sync_playlists.py
2016-11-05 09:18:17.956108 >> Start!
2016-11-05 09:18:17.956108 >> Loading MM.
2016-11-05 09:18:18.301872 >> playlistsongs -> 17425
2016-11-05 09:18:18.306380 >> genres -> 35
2016-11-05 09:18:19.984805 >> songs -> 11114
2016-11-05 09:18:19.992774 >> playlists -> 65
2016-11-05 09:18:20.121853 >> Loading GM.
2016-11-05 09:18:22.670096 >> Logged In Mobileclient: True
2016-11-05 09:18:25.549366 >> songs -> 3683
2016-11-05 09:18:48.460698 >> playlists -> 39
2016-11-05 09:18:48.548233 >> genres -> 22
2016-11-05 09:18:48.589367 >> Syncing playlists!
2016-11-05 09:18:49.261670 >> Updating MM playcount for b'Coldplay -- Yes'. Incrementing by 1 to 164.
2016-11-05 09:18:49.279168 >> Updating MM playcount for b'Coldplay -- Viva La Vida'. Incrementing by 1 to 76.
2016-11-05 09:18:49.295626 >> Updating MM playcount for b'Coldplay -- Violet Hill'. Incrementing by 1 to 171.
2016-11-05 09:18:49.312628 >> Updating MM playcount for b'Coldplay -- Strawberry Swing'. Incrementing by 1 to 230.
2016-11-05 09:18:49.329627 >> Updating MM playcount for b'Coldplay -- Death And All His Friends'. Incrementing by 1 to 133.
2016-11-05 09:18:49.345883 >> Updating MM playcount for b'Coldplay -- Mylo Xyloto'. Incrementing by 1 to 135.
2016-11-05 09:18:49.362561 >> Updating MM playcount for b'Coldplay -- Hurts Like Heaven'. Incrementing by 1 to 139.
2016-11-05 09:18:49.379386 >> Updating MM playcount for b'Coldplay -- Paradise'. Incrementing by 1 to 163.
2016-11-05 09:18:49.395887 >> Updating MM playcount for b'Coldplay -- Charlie Brown'. Incrementing by 1 to 95.
2016-11-05 09:18:49.412575 >> Updating MM playcount for b'Coldplay -- Us Against the World'. Incrementing by 1 to 128.
2016-11-05 09:18:49.429472 >> Updating MM playcount for b'Coldplay -- M.M.I.X.'. Incrementing by 1 to 136.
2016-11-05 09:18:49.446438 >> Updating MM playcount for b'Coldplay -- Birds'. Incrementing by 1 to 31.
2016-11-05 09:18:49.462393 >> Updating MM playcount for b'Coldplay -- Hymn For The Weekend'. Incrementing by 1 to 32.
2016-11-05 09:18:49.479412 >> Synced a_Coldplay!
2016-11-05 09:18:51.483393 >> Updating MM playcount for b'Delerium -- Ritual'. Incrementing by 7 to 10.
2016-11-05 09:18:51.500891 >> Updating MM playcount for b'Delerium -- Seven Gates Of Thebes'. Incrementing by 6 to 11.
2016-11-05 09:18:51.518891 >> Updating MM playcount for b'Delerium -- Ghost Requiem'. Incrementing by 12 to 18.
2016-11-05 09:18:51.536892 >> Updating MM playcount for b'Delerium -- Once In A Lifetime'. Incrementing by 14 to 21.
2016-11-05 09:18:51.554401 >> Updating MM playcount for b'Delerium -- Made To Move'. Incrementing by 14 to 19.
2016-11-05 09:18:51.570901 >> Updating MM playcount for b'Delerium -- Continuum'. Incrementing by 11 to 15.
2016-11-05 09:18:51.588408 >> Updating MM playcount for b'Delerium -- Dark Visions'. Incrementing by 5 to 9.
2016-11-05 09:18:51.604419 >> Synced a_Delerium!
2016-11-05 09:18:51.604905 >> Synced a_DT8 Project!
2016-11-05 09:18:55.978500 >> MM list != GM list
2016-11-05 09:18:55.984640 >> Track Various Artists-M1Live-Heartbreak [M'Black Extended Mix] missing in GM
2016-11-05 09:18:55.985646 >> "Various Artists-M1Live-Heartbreak [M'Black Extended Mix]" not found! Adding...
2016-11-05 09:18:56,442 - gmusicapi.Musicmanager3 (musicmanager:541) [WARNING]: upload of '"D:\\Music\\00 - M'Black - Heartbreak [M'Black Extended Mix].mp3"' rejected: TrackSampleResponse code 4: ALREADY_EXISTS(2bf3e2fd-f849-38f7-9a88-36ff235a729f)
2016-11-05 09:18:56.443380 >> D:\Music\00 - M'Black - Heartbreak [M'Black Extended Mix].mp3 not uploaded! -> TrackSampleResponse code 4: ALREADY_EXISTS(2bf3e2fd-f849-38f7-9a88-36ff235a729f)
2016-11-05 09:18:56.444880 >> g_M1-Live-1 BEST found! Deleting entries...
2016-11-05 09:18:57.732429 >> 214 songs added to playlist g_M1-Live-1 BEST!
2016-11-05 09:18:57.734425 >> Various Artists-M1Live-Heartbreak [M'Black Extended Mix] not found in gm_playlist "g_M1-Live-1 BEST"...
2016-11-05 09:18:57.735430 >> Updating MM playcount for b'Various Artists -- Right Now [Radio Edit] arch001'. Incrementing by 2 to 53.
2016-11-05 09:18:57.764602 >> Updating MM playcount for b'Various Artists -- You da one'. Incrementing by 2 to 67.
2016-11-05 09:18:57.782583 >> Updating MM playcount for b'Various Artists -- Take a bow (Seamus Haji Radio Edit)'. Incrementing by 5 to 55.
2016-11-05 09:18:57.799507 >> Synced g_M1-Live-1 BEST!
2016-11-05 09:18:58.508614 >> g_Study found! Deleting entries...
2016-11-05 09:18:59.794200 >> 252 songs added to playlist g_Study!
2016-11-05 09:18:59.797207 >> Various-25 Classical Favorites-Sousa: The Stars & Stripes Forever not found in gm_playlist "g_Study"...
2016-11-05 09:18:59.797706 >> Synced g_Study!
2016-11-05 09:19:01.328467 >> End!
```

