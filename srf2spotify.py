#!/usr/bin/env python
# encoding: utf-8
"""
Parse SRF playlogs into spotify playlists
"""

import sys
import urllib
import urllib2
import xmltodict
import pprint
from dateutil import parser
import datetime
import json
import spotipy
import spotipy.util as util
import logging
import argparse

def main(argv=None):
  parser = argparse.ArgumentParser(description='Sync feed with spotify playlist')
  parser.add_argument('username',help='spotify username/account to sync the playlist to')
  parser.add_argument('feed',help='podcast feed URL, e.g. http://podcasts.srf.ch/rock_special_mpx.xml')
  parser.add_argument('--id',required=False,default=None,help='spotify playlist ID to sync to. overrides the name below.')
  parser.add_argument('--name',required=False,default=None,help='spotify playlist name to sync to. playlist is created if there is no such playlist. the podcast title is used if omitted.')
  parser.add_argument('-v','--verbose',help='output debug logging',action='store_true')
  args = parser.parse_args()

  if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

  logging.debug("got args: %s" % args)

  token = spotipy.util.prompt_for_user_token(args.username,'playlist-modify-public')
  logging.debug("go auth token")
  spotify = spotipy.Spotify(auth=token)
  logging.debug("logged in to spotify")

  sync_feed_with_playlist(feed=args.feed,spotify=spotify,spotifyusername=args.username,playlist_name=args.name,playlist_id=args.id)


def sync_feed_with_playlist(feed,spotifyusername,spotify,playlist_name=None,playlist_id=None):
  """ Sync a SRF3 podcast feed with a spotify playlist

      Parameters:
        - feed - podcast feed URL, e.g. http://podcasts.srf.ch/rock_special_mpx.xml
        - spotifyusername - your spotify username/account to sync the playlist to
        - spotify - authenticated spotipy object, e.g. spotipy.Spotify(auth=spotipy.util.prompt_for_user_token(spotifyusername,'playlist-modify-public'))
        - playlist_id - spotify playlist to sync the feed to
        - playlist_name - name for the spotify playlist to create/update, if both id and name is empty the RSS feed title is used
  """
  # first get the start/end dates for each episode from the podcast feed
  dates = get_datetime_from_podcast(feed)
  logging.info("got %d datetimes" % len(dates))
  logging.debug(dates)

  # then query the songlog for artist/title during the episode intervals
  songs = []
  for (start,end) in dates:
    songs += get_srf3_songlog(start,end)
  logging.info("got %d songs" % len(songs))
  logging.debug(songs)

  if len(songs) == 0:
    # bail out if the list is empty before removing everything
    sys.exit(1)

  # query spotify for the artist/titles and get the track IDs
  songs = spotify_search_songs(songs,spotify)
  logging.info("got %d unique songs from spotify" % len(songs))
  logging.debug(songs)

  if len(songs) == 0:
    # bail out if the list is empty before removing everything
    sys.exit(1)

  # use the playlist_id if there is one, else use the playlist named like playlist_name or create one like the podcast title
  if not playlist_id:
    if not playlist_name:
      # use the podcast title if nothing specified
      data = get_podcast_data(feed)
      playlist_name = data['rss']['channel']['title']

    # since one can't query for a specific playlist by name we have to get them all and search ourselves
    playlists = spotify.user_playlists(spotifyusername)
    logging.info("Got %d existing playlists for user %s" % (len(playlists),spotifyusername))
    logging.debug(playlists)

    targetplaylist = ""
    for playlist in playlists['items']:
      if playlist['name'] == playlist_name:
        targetplaylist = playlist['uri']
        logging.info("found existing playlist %s %s" % (playlist_name,targetplaylist))
        break
    if targetplaylist == "":
      # the playlist does not exist yet
      playlist = spotify.user_playlist_create(spotifyusername,playlist_name)
      targetplaylist = playlist['uri']
      logging.info("created new playlist %s %s" % (targetplaylist,playlist_name))
  else:
    logging.debug("setting playlist id to %s" % playlist_id)
    targetplaylist = playlist_id

  # there is a spotify.user_playlist_replace_tracks() but it accepts only 100 tracks at a time
  # the rest has to be spotify.user_playlist_add_tracks() manually
  # so we're adding/deleting them ourselves

  # get all old tracks from the playlist to later delete the superfluous ones
  playlisttracks = []
  logging.debug("spotify_get_all_trackids %s %s %s" % (spotifyusername,targetplaylist,spotify))
  for track in spotify_get_all_trackids(spotifyusername,targetplaylist,spotify):
    if track not in songs:
      logging.info("removing %s from playlist" % track)
      spotify.user_playlist_remove_all_occurrences_of_tracks(spotifyusername,targetplaylist,[track])
    else:
      playlisttracks.append(track)

  # add podcast songs not already in the playlist
  for song in songs:
    if song not in playlisttracks:
      logging.info("adding %s to playlist" % song)
      spotify.user_playlist_add_tracks(spotifyusername,targetplaylist,[song])

def spotify_get_all_trackids(spotifyusername,targetplaylist,spotify):
  """ Get all tracks for a playlist - the API only provides 100 tracks at the time

      Parameters:
        - spotifyusername - spotify account to look for the playlist
        - targetplaylist - playlist ID
        - spotify - authenticated spotipy object
  """
  logging.info("getting full list of tracks for %s" % targetplaylist)
  playlist = spotify.user_playlist(spotifyusername,targetplaylist)
  result = []
  while len(result) < playlist['tracks']['total']:
    logging.info("querying offset=%d of %d" % (len(result),playlist['tracks']['total']))
    playlistitems = spotify.user_playlist_tracks(spotifyusername,targetplaylist,offset=len(result))
    for item in playlistitems['items']:
      result.append(item['track']['uri'])
  return result

def spotify_search_songs(songs,spotify=spotipy.Spotify()):
  """ search spotify for artist/title and return the unique spotify track IDs

      Parameters:
        - songs - iterable of mapping (e.g. array of hash) with keys 'artist' and 'title'
        - spotify - spotipy object, doesn't need to be authenticated for search (although there is a higher rate limit for authenticated users)
  """
  results = []
  for song in songs:
    result = spotify.search("artist:"+song['artist']+" track:"+song['title'],limit=1,type='track')
    if len(result['tracks']['items']) > 0:
      track = result['tracks']['items'][0]['uri']
      if track not in results:
        results.append(track)
    else:
      logging.info("no spotify track found for %s" % song)
  return results

def get_srf3_songlog(start,end,datapollingurl="http://ws.srf.ch/songlog/log/channel/",datachannelid="dd0fa1ba-4ff6-4e1a-ab74-d7e49057d96f"):
  """ Get the song log for SRF3 radio by start/end datetime. Returns an array of dict with 'artist' and 'title' keys"""
  # example lookup from http://www.srf.ch/sendungen/rock-special/the-shit-kalifornien-bern-einfach for SRF3
  # http://ws.srf.ch/songlog/log/channel/dd0fa1ba-4ff6-4e1a-ab74-d7e49057d96f.json?callback=songLogPollerCallback_episode_fullview&fromDate=2015-10-28T20%3A03%3A00&toDate=2015-10-28T22%3A00%3A00&page.size=100&page.page=0&page.sort=playedDate&page.sort.dir=desc
  params = {
    'fromDate': start.strftime("%Y-%m-%dT%H:%M:%S"),
    'toDate': end.strftime("%Y-%m-%dT%H:%M:%S")
  }
  url = datapollingurl + datachannelid + ".json?" + urllib.urlencode(params)
  filehandle = urllib2.urlopen(url)
  data = filehandle.read()
  filehandle.close()
  data = json.loads(data)
  songs = []
  for song in data['Songlog']:
    songs.append({'title': song['Song']['title'], 'artist': song['Song']['Artist']['name']})
  return songs

def get_datetime_from_podcast(feed):
  """return the (start,end) datetime for episodes from the podcast feed pubDate (=episode ending time) and rounded duration"""
  data = get_podcast_data(feed)
  dates = []
  for episode in data['rss']['channel']['item']:
    # pubDate: Wed, 28 Oct 2015 22:00:00 +0100
    # itunes:duration: 6590 (seconds)
    end = parser.parse(episode['pubDate'])
    start = end - datetime.timedelta(hours=round(float(episode['itunes:duration'])/3600))
    dates.append((start,end))
  return dates

def get_podcast_data(feed):
  """Load Podcast from feed URL and parse XML into dict"""
  filehandle = urllib2.urlopen(feed)
  data = filehandle.read()
  filehandle.close()
  return xmltodict.parse(data)

if __name__ == "__main__":
  """Boilerplate main function call"""
  sys.exit(main(sys.argv))
