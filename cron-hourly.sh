#!/bin/sh
# sync the jouluradio feeds hourly since the last20-sing-feeds cover about an hour of airtime, the resulting spotify playlists are public so you can just use them

# set the spotify-credentials from the environment variable, see README
echo $SPOTIPY_CACHE > .cache-$SPOTIFY_USERNAME

python jouluradio2spotify.py -av --id 3W2gEbnEqytlM221BSusCb $SPOTIFY_USERNAME http://www.jouluradio.fi/biisilista/jouluradiolast20.json
# https://open.spotify.com/user/aarnoaukia/playlist/3W2gEbnEqytlM221BSusCb

python jouluradio2spotify.py -av --id 4KXmZgDJG5J4MMDIM5wSAt $SPOTIFY_USERNAME http://www.jouluradio.fi/biisilista/jouradiolast20.json
# https://open.spotify.com/user/aarnoaukia/playlist/4KXmZgDJG5J4MMDIM5wSAt

python jouluradio2spotify.py -av --id 3HY2gCw7bfyxK4TtbeHb4s $SPOTIFY_USERNAME http://www.jouluradio.fi/biisilista/Rouhea_Joululast20.json
# https://open.spotify.com/user/aarnoaukia/playlist/3HY2gCw7bfyxK4TtbeHb4s

python jouluradio2spotify.py -av --id 75oYEbhELvE36eIsT4sDzJ $SPOTIFY_USERNAME http://www.jouluradio.fi/biisilista/Kauneimmatlast20.json
# https://open.spotify.com/user/aarnoaukia/playlist/75oYEbhELvE36eIsT4sDzJ

python jouluradio2spotify.py -av --id 5JXXR8XDKMWrZvdsbmbnLO $SPOTIFY_USERNAME http://www.jouluradio.fi/biisilista/pikkulast20.json
# https://open.spotify.com/user/aarnoaukia/playlist/5JXXR8XDKMWrZvdsbmbnLO

python jouluradio2spotify.py -av --id 11GKkK9iKKWP4Y0zV9teo7 $SPOTIFY_USERNAME http://www.jouluradio.fi/biisilista/klassinenjoululast20.json
# https://open.spotify.com/user/aarnoaukia/playlist/11GKkK9iKKWP4Y0zV9teo7
