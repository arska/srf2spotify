#!/usr/bin/env python
# encoding: utf-8
"""
Parse jouluradio.fi playlogs into spotify playlists
"""

import sys
import spotipy
import spotipy.util as util
import logging
import argparse
import os.path
from any2spotify import *

def main(argv=None):
  parser = argparse.ArgumentParser(description='Sync feed with spotify playlist')
  parser.add_argument('username',help='spotify username/account to sync the playlist to')
  parser.add_argument('feed',help='playlog URL, e.g. http://www.jouluradio.fi/biisilista/jouluradiolast20.json')
  parser.add_argument('--id',required=False,default=None,help='spotify playlist ID to sync to. overrides the playlist name below.')
  parser.add_argument('--name',required=False,default=None,help='spotify playlist name to sync to. the playlist is created if there is no such playlist for the user. the feed title is used if omitted.')
  parser.add_argument('-v','--verbose',help='output debug logging',action='store_true',default=False)
  parser.add_argument('-a','--add',help='only add songs to the playlist, dont remove them if missing from the feed',action='store_true',default=False)
  parser.add_argument('-l','--limit',help='limit the total number of tracks in the playist (useful with --add, default=0=no limit)',default=0)
  args = parser.parse_args()

  if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)

  logging.debug("got args: %s" % args)

  token = spotipy.util.prompt_for_user_token(args.username,'playlist-modify-public')
  logging.debug("go auth token")
  spotify = spotipy.Spotify(auth=token)
  logging.debug("logged in to spotify")

  songs = spotify_search_songs(get_jouluradio_songlog(url=args.feed))

  if args.id:
    targetplaylist = args.id
  else:
    if not args.name:
      args.name = os.path.basename(args.feed)
    targetplaylist = get_or_create_playlistid_by_name(args.name,args.username,spotify)

  sync_tracks(songs,targetplaylist,args.username,spotify,addonly=args.add,limit=args.limit)

if __name__ == "__main__":
  """Boilerplate main function call"""
  sys.exit(main(sys.argv))

