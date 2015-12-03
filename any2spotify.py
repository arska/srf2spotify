#!/usr/bin/env python
# encoding: utf-8
"""
Common functions for spotify playlist import
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
import HTMLParser
import cachetools

cache = cachetools.LRUCache(1000)

def sync_podcastfeed_with_playlist(feed,spotifyusername,spotify,playlist_name=None,playlist_id=None,addonly=False,limit=0):
  """ Sync a SRF3 podcast feed with a spotify playlist

      Parameters:
        - feed - podcast feed URL, e.g. http://podcasts.srf.ch/rock_special_mpx.xml
        - spotifyusername - your spotify username/account to sync the playlist to
        - spotify - authenticated spotipy object, e.g. spotipy.Spotify(auth=spotipy.util.prompt_for_user_token(spotifyusername,'playlist-modify-public'))
        - playlist_id - spotify playlist to sync the feed to
        - playlist_name - name for the spotify playlist to create/update, if both id and name is empty the RSS feed title is used
        - addonly - only add songs to the playlist, dont remove them from the playlist if missing from the feed
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

  if playlist_id:
    targetplaylist = playlist_id
  else:
    if not playlist_name:
      # use the podcast title if nothing specified
      data = get_podcast_data(feed)
      playlist_name = data['rss']['channel']['title']

    targetplaylist = get_or_create_playlistid_by_name(playlist_name,spotifyusername,spotify)

    sync_tracks(songs,targetplaylist,spotifyusername,spotify,addonly,limit)

def sync_tracks(songs,targetplaylist,spotifyusername,spotify=spotipy.Spotify,addonly=False,limit=0):
  """ sync a list of spotify song IDs with a spotify playlist

      Parameters:
        - songs - the list of spotify song IDs
        - targetplaylist - the ID of the playlist to sync to
        - spotifyusername - spotify account to look for the playlist¬
        - spotify - authenticated spotipy object¬
        - addonly - only add songs to the spotify playlist, don't remove superfluous tracks
        - limit - limit the total length of the spotify playlist, useful with addonly, removes the oldest tracks
  """
  # there is a spotify.user_playlist_replace_tracks() but it accepts only 100 tracks at a time
  # the rest has to be spotify.user_playlist_add_tracks() manually
  # so we're adding/deleting them ourselves

  # iterate though the playlist and (optionally) delete no longer existing tracks
  playlisttracks = []
  logging.debug("spotify_get_all_trackids %s %s %s" % (spotifyusername,targetplaylist,spotify))
  for track in spotify_get_all_trackids(spotifyusername,targetplaylist,spotify):
    if track not in songs:
      if addonly:
        logging.info("not removing %s since --add is specified" % track)
      else:
        logging.info("removing %s from playlist because not in feed" % track)
        spotify.user_playlist_remove_all_occurrences_of_tracks(spotifyusername,targetplaylist,[track])
    else:
      playlisttracks.append(track)

  # add podcast songs not already in the playlist
  for song in songs:
    if song not in playlisttracks:
      logging.info("adding %s to playlist" % song)
      spotify.user_playlist_add_tracks(spotifyusername,targetplaylist,[song])

  if limit>0:
    # aggregate the existing playlisttracks and the newly added songs to have the new total number
    playlisttracks.extend(songs)
    # only leave the last $limit songs, remove len(playlisttracks)-limit tracks from the start
    for track in playlisttracks[:-limit]:
      logging.info("removing %s from playlist because over limit" % track)
      spotify.user_playlist_remove_all_occurrences_of_tracks(spotifyusername,targetplaylist,[track])

def get_or_create_playlistid_by_name(playlist_name,spotifyusername,spotify):
  """ get a playlist ID from the playlist name of a user, create the playlist if there is none

      Parameters:
        - playlist_name - the name of the playlist to get or create
        - spotifyusername - spotify account to look for the playlist¬
        - spotify - authenticated spotipy object¬
  """

  # since one can't query for a specific playlist by name we have to get them all and search ourselves
  playlists = spotify.user_playlists(spotifyusername)
  logging.info("Got %d existing playlists for user %s" % (len(playlists),spotifyusername))
  logging.debug(playlists)

  for playlist in playlists['items']:
    if playlist['name'] == playlist_name:
      logging.info("found existing playlist %s %s" % (playlist['uri'],playlist_name))
      return playlist['uri']
  # the playlist does not exist yet
  playlist = spotify.user_playlist_create(spotifyusername,playlist_name)
  logging.info("created new playlist %s %s" % (playlist['uri'],playlist_name))
  return playlist['uri']

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

def spotify_search_songs(songs,spotify=spotipy.Spotify(),alternative=False):
  """ search spotify for artist/title and return the unique spotify track IDs

      Parameters:
        - songs - iterable of mapping (e.g. array of hash) with keys 'artist' and 'title'
        - spotify - spotipy object, doesn't need to be authenticated for search (although there is a higher rate limit for authenticated users)
  """
  results = []
  for song in songs:
    #result = spotify.search('artist:'+normalize_name(song['artist'])+' track:'+normalize_name(song['title'])+'',limit=1,type='track')
    #result = spotify.search(''+normalize_name(song['artist'],alternative)+' '+normalize_name(song['title'],alternative)+'',limit=1,type='track')
    result = cached_search(''+normalize_name(song['artist'],alternative)+' '+normalize_name(song['title'],alternative)+'',type='track',spotify=spotify)
    if len(result['tracks']['items']) > 0:
      track = result['tracks']['items'][0]['uri']
      if track not in results:
        results.append(track)
    elif alternative == False:
      track = spotify_search_songs([song],spotify,True) # try alternative normalization
      if len(track) > 0 and track not in results:
        results.extend(track)
    else:
      logging.warning("no spotify track found for %s: %s" % (song,result))
  return results

def cached_search(query,type,spotify):
  key = cachetools.hashkey(query,type)
  if key not in cache:
    logging.debug("search cache miss: %s"%query)
    cache[key] = spotify.search(query,type=type,limit=1)
  return cache[key]

def normalize_name(text,alternative=False):
  html = HTMLParser.HTMLParser()
  return html.unescape(text).encode('utf8').replace('`',(' ' if alternative else '')).replace('\xc2\xb4',(' ' if alternative else '')).replace(' (Radio Edit)','').replace(' (Radio edit)','').replace("'n'",'')

def get_radiorock_songlog(url="http://www.radiorock.fi/api/programdata/getlatest"):
  """ Get the song log for radiorock.fi. Returns an array of dict with 'artist' and 'title' keys"""
  filehandle = urllib2.urlopen(url)
  data = filehandle.read()
  filehandle.close()
  data = json.loads(data)
  songs = []
  for song in data['result']:
    date = datetime.datetime.fromtimestamp(song['timestamp']/1000)
    #logging.debug("%s %s  %s %s" % (date,song['timestamp'],song['song'],song['artist']))
    songs.append({'title': (song['song']), 'artist': (song['artist']), 'timestamp': song['timestamp']})
  return songs

def get_playlist_for_timestamp(timestamp,map):
  """ select the playlist for a msec-timestamp from a map of weekday/time """
  playtime = datetime.datetime.fromtimestamp(timestamp/1000)
  for entry in map:
    #logging.debug("timestamp %s (%s) weekday %s time %s checking %s"%(playtime,timestamp,playtime.weekday(),playtime.time(),entry))
    if (entry['weekday'] == "*" or int(entry['weekday']) == int(playtime.weekday())) and entry['from'] <= playtime.time() and playtime.time() < entry['to']:
      logging.debug("timestamp %s (%s) selected %s" % (playtime,timestamp,entry))
      return entry['playlist']
  logging.info("couldnt find playlist for %s (%s), selecting last from map" % (playtime,timestamp))
  return map[-1]['playlist']

def get_jouluradio_songlog(url="http://www.jouluradio.fi/biisilista/jouluradiolast20.json"):
  """ Get the song log for jouluradio.fi. Returns an array of dict with 'artist' and 'title' keys"""
  filehandle = urllib2.urlopen(url)
  data = filehandle.read()
  filehandle.close()
  data = json.loads(data)
  songs = []
  for song in data['last20']:
    songs.append({'title': (song['song']), 'artist': (song['artist'])})
  return songs

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
    songs.append({'title': (song['Song']['title']), 'artist': (song['Song']['Artist']['name'])})
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

