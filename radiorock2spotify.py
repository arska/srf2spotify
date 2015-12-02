#!/usr/bin/env python
# encoding: utf-8
"""
Parse radiorock.fi playlogs into spotify playlists
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
  parser.add_argument('username',help='spotify username/account to sync the playlist to',default="aarnoaukia")
  parser.add_argument('feed',help='playlog URL, e.g. http://www.radiorock.fi/api/programdata/getlatest',default="http://www.radiorock.fi/api/programdata/getlatest")
  #parser.add_argument('--id',required=False,default=None,help='spotify playlist ID to sync to. overrides the playlist name below.')
  #parser.add_argument('--name',required=False,default=None,help='spotify playlist name to sync to. the playlist is created if there is no such playlist for the user. the feed title is used if omitted.')
  parser.add_argument('-v','--verbose',help='output debug logging',action='store_true',default=False)
  parser.add_argument('-a','--add',help='only add songs to the playlist, dont remove them if missing from the feed',action='store_true',default=False)
  parser.add_argument('-l','--limit',help='limit the total number of tracks in the playist (useful with --add, default=0=no limit)',default=0)
  args = parser.parse_args()

  if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

  logging.debug("got args: %s" % args)

  token = spotipy.util.prompt_for_user_token(args.username,'playlist-modify-public')
  logging.debug("go auth token")
  spotify = spotipy.Spotify(auth=token)
  logging.debug("logged in to spotify")

  # from the feed we get about 72h of playlogs, but no indication what program was running at the time to split it up
  # so here is the map how to split them up
  playlistmap = [
    {
      'weekday': '2', #ke
      'from': datetime.time(19),
      'to': datetime.time(21),
      'playlist': 'spotify:user:aarnoaukia:playlist:6jkZf1uscq2AwGWKf7To0w',
    },
    {
      'weekday': '3', #to
      'from': datetime.time(19),
      'to': datetime.time(21),
      'playlist': 'spotify:user:aarnoaukia:playlist:4OdqoyHT3mVndTwwrEhMjp',
    },
    {
      'weekday': '4', #pe
      'from': datetime.time(19),
      'to': datetime.time(21),
      'playlist': 'spotify:user:aarnoaukia:playlist:5JmDRoineh4NuGjYD5zOvb',
    },
    {
      'weekday': '5', #la
      'from': datetime.time(18),
      'to': datetime.time(19),
      'playlist': 'spotify:user:aarnoaukia:playlist:3PObJM8VTktdZE4kBH79xo',
    },
    {
      'weekday': '*', #kaikki muut päivät
      'from': datetime.time(0),
      'to': datetime.time(23,59,59),
      'playlist': 'spotify:user:aarnoaukia:playlist:5BEhl8eSv2l1DRECv8DXAH',
    },
  ]

  songmap = {}
  for song in get_radiorock_songlog():
    playlist = get_playlist_for_timestamp(song['timestamp'],playlistmap)
    if playlist not in songmap:
      songmap[playlist] = []
    songmap[playlist].append(song)
  for playlist in songmap.keys():
    sync_tracks(spotify_search_songs(songmap[playlist],spotify),playlist,args.username,spotify,addonly=args.add,limit=args.limit)

if __name__ == "__main__":
  """Boilerplate main function call"""
  sys.exit(main(sys.argv))

