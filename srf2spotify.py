#!/usr/bin/env python
# encoding: utf-8
"""
Parse SRF playlogs into spotify playlists
"""

import sys
#import urllib
#import urllib2
#import xmltodict
#import pprint
#from dateutil import parser
#import datetime
#import json
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
  args = parser.parse_args()

  if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

  logging.debug("got args: %s" % args)

  token = spotipy.util.prompt_for_user_token(args.username,'playlist-modify-public')
  logging.debug("go auth token")
  spotify = spotipy.Spotify(auth=token)
  logging.debug("logged in to spotify")

  sync_podcastfeed_with_playlist(feed=args.feed,spotify=spotify,spotifyusername=args.username,playlist_name=args.name,playlist_id=args.id,addonly=args.add)

if __name__ == "__main__":
  """Boilerplate main function call"""
  sys.exit(main(sys.argv))

