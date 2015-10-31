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

def main(argv=None):
  if argv is None:
    argv = sys.argv
  feed = "http://podcasts.srf.ch/rock_special_mpx.xml"
  spotifyusername = "aarnoaukia"
  spotifyauthscope = 'playlist-modify-public playlist-modify-private'
  playlistname = "SRF Rock Special"
  logging.basicConfig(level=logging.DEBUG)

  dates = get_datetime_from_podcast(feed)
  logging.info("got %d datetimes" % len(dates))
  logging.debug(dates)

  songs = []
  for (start,end) in dates:
    songs += get_srf3_songlog(start,end)
  logging.info("got %d songs" % len(songs))
  logging.debug(songs)

  token = spotipy.util.prompt_for_user_token(spotifyusername,spotifyauthscope)
  logging.debug("go auth token %s" % token)
  spotify = spotipy.Spotify(auth=token)
  logging.debug("logged in to spotify")

  songs = spotify_search_songs(songs,spotify)
  logging.info("got %d unique songs from spotify" % len(songs))
  logging.debug(songs)

  playlists = spotify.user_playlists(spotifyusername)
  logging.info("Got %d existing playlists" % len(playlists))
  logging.debug(playlists)
  targetplaylist = ""
  for playlist in playlists['items']:
    if playlist['name'] == playlistname:
      targetplaylist = playlist['uri']
      logging.info("found existing playlist %s %s" % (playlistname,targetplaylist))
      break
  if targetplaylist == "":
    # the playlist does not exist yet
    playlist = spotify.user_playlist_create(spotifyusername,playlistname)
    targetplaylist = playlist['uri']
    logging.info("created new playlist %s %s" % (targetplaylist,playlistname))

  playlisttracks = []
  for track in spotify_get_all_trackids(spotifyusername,targetplaylist,spotify):
    if track not in songs:
      logging.info("removing %s from playlist" % track['uri'])
      spotify.user_playlist_remove_all_occurrences_of_tracks(spotifyusername,targetplaylist,track['uri'])
    else:
      playlisttracks.append(track)

  for song in songs:
    if song not in playlisttracks:
      logging.info("adding %s to playlist" % song)
      spotify.user_playlist_add_tracks(spotifyusername,targetplaylist,[song])

def spotify_get_all_trackids(spotifyusername,targetplaylist,spotify):
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
  results = []
  for song in songs:
    result = spotify.search("artist:"+song['artist']+" track:"+song['title'],limit=1,type='track')
    if len(result['tracks']['items']) > 0:
      track = result['tracks']['items'][0]['uri']
      if track not in results:
        results.append(track)
  return results

def get_srf3_songlog(start,end):
  # http://ws.srf.ch/songlog/log/channel/dd0fa1ba-4ff6-4e1a-ab74-d7e49057d96f.json?callback=songLogPollerCallback_episode_fullview&fromDate=2015-10-28T20%3A03%3A00&toDate=2015-10-28T22%3A00%3A00&page.size=100&page.page=0&page.sort=playedDate&page.sort.dir=desc
  datapollingurl="http://ws.srf.ch/songlog/log/channel/"
  datachannelid="dd0fa1ba-4ff6-4e1a-ab74-d7e49057d96f"
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
  filehandle = urllib2.urlopen(feed)
  data = filehandle.read()
  filehandle.close()
  data = xmltodict.parse(data)
  dates = []
  for episode in data['rss']['channel']['item']:
    # pubDate: Wed, 28 Oct 2015 22:00:00 +0100
    # itunes:duration: 6590 (seconds)
    end = parser.parse(episode['pubDate'])
    start = end - datetime.timedelta(hours=round(float(episode['itunes:duration'])/3600))
    dates.append((start,end))
  return dates

if __name__ == "__main__":
  """Boilerplate main function call"""
  sys.exit(main())
