# Spotify playlist sync/update

This project started with SRF2spotify, later jouluradio2spotify was added

## SRF2Spotify

Swiss radio SRF has a nicely compiled weekly "rock special" programme that I have been listening to as podcast. I'd like to create a playlist and shuffle though the songs in spotify.

### playlists
* feel free to subscribe to the spotify playlists:
  * SRF3 Black Music Special: https://open.spotify.com/user/aarnoaukia/playlist/6Mcg2gNk9b9u9g2HCmUcy5
  * SRF3 Pop Routes: https://open.spotify.com/user/aarnoaukia/playlist/4sq8otplfToytYMevleTBi
  * SRF3 Sounds: https://open.spotify.com/user/aarnoaukia/playlist/5KfO8EsKEX0T0mjbJmHaMD
  * SRF3 Rock Special: https://open.spotify.com/user/aarnoaukia/playlist/4Uxp8OaU8Fc06cjpQgZxdt
  * SRF3 CH Special: https://open.spotify.com/user/aarnoaukia/playlist/72i3UMC1LDoi5auo9AACvH
  * SRF3 Hitparade: https://open.spotify.com/user/aarnoaukia/playlist/1UH2A80CsXn0Cp5njr8x0E
  * SRF3 Reggae Special: https://open.spotify.com/user/aarnoaukia/playlist/0mdijROnuU2CRY7MKcDv35
  * SRF3 World Music Special: https://open.spotify.com/user/aarnoaukia/playlist/3K9MLAIkBey8i1GSCQ95NF

### usage
see `python srf2spotify.py -h` for parameter usage

* `pip install -r requirements.txt`
* register yourself at https://developer.spotify.com/my-applications, enter "http://localhost/" for the "Redirect URIs" (it is fine if you don't have a webserver running)
* create an `.env` file with the following contents:
```
SPOTIPY_CLIENT_ID='your client ID from developer.spotify.com'
SPOTIPY_CLIENT_SECRET='your client secret from developer.spotify.com'
SPOTIPY_REDIRECT_URI='http://localhost/'
SPOTIPY_CACHE=''
SPOTIFY_USERNAME='your spotify username'
```
* run the script with `env $(cat .env | xargs) python srf2spotify.py $SPOTIFY_USERNAME <podcast feed url>` (see more options with -h)
* when first run the script will ask you to authorize the client_id for your spotifyusername by visiting a spotify URL (you will be asked if you want to allow your developer account to access your spotify account), then you will be redirected to your SPOTIPY_REDIRECT_URI with the authorization code appended, e.g. http://localhost/?code=..., copy-and-paste that URL to the terminal
* copy the contents of `.cache-<spotifyusername>` (`{"access_token": ...}`) into `SPOTIPY_CACHE='{"access_token": ...}'` in `.env` (this is only needed if you want to run `heroku local` or cron.sh)

### result
* see cron.sh for examples
* the examples are run daily on a heroku free instance

## Jouluradio2spotify
In Xmas-time there is a finnish radio playing only Xmas-music
### usage
see above for details, see cron-hourly.sh for examples
### result
* the feeds are updated hourly

* Jouluradio.fi 2015 (finnish): https://open.spotify.com/user/aarnoaukia/playlist/3W2gEbnEqytlM221BSusCb
* Jouluradio.fi Xmas 2015 (english): https://open.spotify.com/user/aarnoaukia/playlist/4KXmZgDJG5J4MMDIM5wSAt
* Jouluradio.fu Rouhea Joulu 2015 ("corny/juicy"): https://open.spotify.com/user/aarnoaukia/playlist/3HY2gCw7bfyxK4TtbeHb4s
