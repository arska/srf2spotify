#!/bin/sh
# sync the swiss radio feeds daily, the resulting spotify playlists are public so you can just use them

# set the spotify-credentials from the environment variable, see README
echo $SPOTIPY_CACHE > .cache-$SPOTIFY_USERNAME

# abort if one of the commands fail to check the logs
set -e

python srf2spotify.py -a $@ --id 6Mcg2gNk9b9u9g2HCmUcy5 $SPOTIFY_USERNAME http://podcasts.srf.ch/black-music_special_mpx.xml
# https://open.spotify.com/user/$SPOTIFY_USERNAME/playlist/6Mcg2gNk9b9u9g2HCmUcy5

python srf2spotify.py -a $@ --id 4sq8otplfToytYMevleTBi $SPOTIFY_USERNAME http://podcasts.srf.ch/pop_routes_mpx.xml
# https://open.spotify.com/user/$SPOTIFY_USERNAME/playlist/4sq8otplfToytYMevleTBi

python srf2spotify.py -a $@ --id 5KfO8EsKEX0T0mjbJmHaMD $SPOTIFY_USERNAME http://podcasts.srf.ch/sounds_mpx.xml
# https://open.spotify.com/user/$SPOTIFY_USERNAME/playlist/5KfO8EsKEX0T0mjbJmHaMD

python srf2spotify.py -a $@ --id 4Uxp8OaU8Fc06cjpQgZxdt $SPOTIFY_USERNAME http://podcasts.srf.ch/rock_special_mpx.xml
# https://open.spotify.com/user/$SPOTIFY_USERNAME/playlist/4Uxp8OaU8Fc06cjpQgZxdt

python srf2spotify.py -a $@ --id 72i3UMC1LDoi5auo9AACvH $SPOTIFY_USERNAME http://podcasts.srf.ch/ch_special_mpx.xml
# https://open.spotify.com/user/aarnoaukia/playlist/72i3UMC1LDoi5auo9AACvH

python srf2spotify.py -a $@ --id 1UH2A80CsXn0Cp5njr8x0E $SPOTIFY_USERNAME http://podcasts.srf.ch/hitparade_mpx.xml
# https://open.spotify.com/user/aarnoaukia/playlist/1UH2A80CsXn0Cp5njr8x0E

python srf2spotify.py -a $@ --id 0mdijROnuU2CRY7MKcDv35 $SPOTIFY_USERNAME http://podcasts.srf.ch/reggae_special_mpx.xml
# https://open.spotify.com/user/aarnoaukia/playlist/0mdijROnuU2CRY7MKcDv35

python srf2spotify.py -a $@ --id 3K9MLAIkBey8i1GSCQ95NF $SPOTIFY_USERNAME http://podcasts.srf.ch/world_music_special_mpx.xml
# https://open.spotify.com/user/aarnoaukia/playlist/3K9MLAIkBey8i1GSCQ95NF

python radiorock2spotify.py -a $@ $SPOTIFY_USERNAME http://www.radiorock.fi/api/programdata/getlatest
# see code or README.md for links
