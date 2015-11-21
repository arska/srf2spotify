# SRF2Spotify

Swiss radio SRF has a nicely compiled weekly "rock special" programme that I have been listening to as podcast. I'd like to create a playlist and shuffle though the songs in spotify.

## playlists
if you just want to listen to the resulting playlists in spotify you'll find the links in `cron.sh`

## usage
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

## result
* see cron.sh for examples
* the examples are run daily on a heroku free instance
* feel free to subscribe to the spotify playlists linked