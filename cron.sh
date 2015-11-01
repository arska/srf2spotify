#!/bin/sh

echo $SPOTIPY_CACHE > .cache-$SPOTIFY_USERNAME

python srf2spotify.py $SPOTIFY_USERNAME http://podcasts.srf.ch/black-music_special_mpx.xml
# https://open.spotify.com/user/$SPOTIFY_USERNAME/playlist/6Mcg2gNk9b9u9g2HCmUcy5

python srf2spotify.py $SPOTIFY_USERNAME http://podcasts.srf.ch/pop_routes_mpx.xml
# https://open.spotify.com/user/$SPOTIFY_USERNAME/playlist/4sq8otplfToytYMevleTBi

python srf2spotify.py $SPOTIFY_USERNAME http://podcasts.srf.ch/sounds_mpx.xml
# https://open.spotify.com/user/$SPOTIFY_USERNAME/playlist/5KfO8EsKEX0T0mjbJmHaMD

python srf2spotify.py $SPOTIFY_USERNAME http://podcasts.srf.ch/rock_special_mpx.xml
# https://open.spotify.com/user/$SPOTIFY_USERNAME/playlist/4Uxp8OaU8Fc06cjpQgZxdt
