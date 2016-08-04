#!/usr/bin/env python
# encoding: utf-8
"""
Parse SRF playlogs into spotify playlists
"""

import sys
import spotipy
import spotipy.util as util
import logging
import argparse
from any2spotify import *

def main(argv=None):
  parser = argparse.ArgumentParser(description='Sync feed with spotify playlist')
  parser.add_argument('username',help='spotify username/account to sync the playlist to')
  parser.add_argument('feed',help='podcast feed URL, e.g. http://podcasts.srf.ch/rock_special_mpx.xml')
  parser.add_argument('--id',required=False,default=None,help='spotify playlist ID to sync to. overrides the playlist name below.')
  parser.add_argument('--name',required=False,default=None,help='spotify playlist name to sync to. the playlist is created if there is no such playlist for the user. the podcast title is used if omitted.')
  parser.add_argument('-v','--verbose',help='output debug logging',action='store_true',default=False)
  parser.add_argument('-a','--add',help='only add songs to the playlist, dont remove them if missing from the feed',action='store_true',default=False)
  parser.add_argument('-l','--limit',help='limit the total number of tracks in the playist (useful with --add, default=0=no limit)',default=0)
  args = parser.parse_args()

logformat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

if args.verbose:
    logging.basicConfig(level=logging.DEBUG, format=logformat)
else:
    logging.basicConfig(level=logging.INFO, format=logformat)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)

  logging.debug(args)

  token = spotipy.util.prompt_for_user_token(args.username,'playlist-modify-public')
  spotify = spotipy.Spotify(auth=token)

  sync_podcastfeed_with_playlist(feed=args.feed,spotify=spotify,spotifyusername=args.username,playlist_name=args.name,playlist_id=args.id,addonly=args.add,limit=args.limit)

if __name__ == "__main__":
  """Boilerplate main function call"""
  sys.exit(main(sys.argv))

