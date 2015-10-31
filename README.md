# SRF2Spotify

Swiss radio SRF has a nicely compiled weekly "rock special" programme that I have been listening to as podcast. I'd like to create a playlist and shuffle though the songs in spotify.

## usage
1. register yourself at https://developer.spotify.com/my-applications, enter "http://localhost/" for the "Redirect URIs" (it is fine if you don't have a webserver running)
2. create a ".env" file with the following contents:
> SPOTIPY_CLIENT_ID='<Client ID from above>'
> SPOTIPY_CLIENT_SECRET='<Client Secret from above>'
> SPOTIPY_REDIRECT_URI='http://localhost/'
3. run the script with =env $(cat .env | xargs) python srf2spotify.py <spotifyusername> <podcast feed url>= (see more options with -h)
4. if you are missing some libraries add them with =sudo -H pip install <modulename>=
4. the script will ask you to authorize the client_id for your spotifyusername by visiting a spotify URL that will redirect to the URI above with the authorization code, e.g. http://localhost/?code=..., that you need to copy/paste to the script.
5. the authorization will be saved in ".cache-<spotifyusername>"
6. 