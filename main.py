import sys
import spotipy
import spotipy.util as util
import os
from os import path
from selenium import webdriver
from spotipy import oauth2
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



client_id = "4eacb90864a74bc49e17a90d591723d7"
client_secret = "f22221c21ede49e989f67e69ff5d4db6"
redirect_uri = "http://localhost:3000/redirect"
scope = 'playlist-read-private playlist-read-collaborative'




def update_playlist_entry(playlistJSON, isNew):
    def insert_tracks_newPlaylist(tracks, songList):
        for i, item in enumerate(tracks['items']):
            track = item['track']
            # print playlistJSON[playlist['name']][0][0]
            songList.append({
                track['id']: track['artists'][0]['name'] + " - " + track['name']
            })

            # if track['id'] not in playlistJSON[playlist['name']][1]:
            #     playlistJSON[playlist['name']][0]['songs'].append({
            #         track['id']: track['artists'][0]['name'] + " - " + track['name']
            #     })
                # print "added: " + track['id']

    def insert_new_tracks(tracks, songList):
        # for i, item in enumerate(tracks['items']):
        #     track = item['track']
        print songList[0]

    playlistJSON[playlist['name']] = []
    playlistJSON[playlist['name']].append({
        'numOfSongs':playlist['tracks']['total']
    })
    songList = []
    # print len(playlistJSON[playlist['name']])
    results = sp.user_playlist(username, playlist['id'],fields="tracks,next")
    tracks = results['tracks']


    if isNew:
        insert_tracks_newPlaylist(tracks,songList)
        while tracks['next']:
            tracks = sp.next(tracks)
            insert_tracks_newPlaylist(tracks,songList)

        playlistJSON[playlist['name']].append({
            'songs': songList
        })
    else:
        # insert_new_tracks(tracks,playlistJSON[playlist['name']][0])
        print playlistJSON

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print "Usage: %s username" % (sys.argv[0],)
    sys.exit()


#section modified from: https://github.com/plamere/spotipy/blob/master/spotipy/util.py#L18
#and https://github.com/plamere/spotipy/blob/master/spotipy/oauth2.py


cache_path = None or ".cache-" + username
sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope, cache_path=cache_path)

token_info = sp_oauth.get_cached_token()

if not token_info:
    driver = webdriver.Chrome(executable_path='/home/vergil/Desktop/chromedriver/chromedriver')
    driver.get(sp_oauth.get_authorize_url())

    wait = WebDriverWait(driver, 10)
    wait.until(EC.title_is("localhost"))

    token = sp_oauth.get_access_token(sp_oauth.parse_response_code(driver.current_url))['access_token']

    driver.close()
if token_info:
    token = token_info['access_token']


if token:
    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(username)



    # playlistJSON = {}
    if not path.exists("downloadLog.json"):
        open("downloadLog.json","w+")

    if os.stat("downloadLog.json").st_size != 0:
        with open("downloadLog.json", "r") as input:
            playlistJSON = json.load(input)
    else:
        playlistJSON = {}



    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            if playlist['name'] == "tester":
                if playlist['name'] in playlistJSON:             #TODO: fix playlist name repeats, input (3) change to ID?
                    print playlist['name']
                    print '  total tracks', playlist['tracks']['total']
                    print "playlist already following"
                    if playlist['tracks']['total'] != playlistJSON[playlist['name']][0]['numOfSongs']:
                        print " -- new songs added"                 #TODO: or removed!! (2)
                    #     update_playlist_entry(playlistJSON,0)     #TODO: update playlist songList (1)
                else:
                    print "New playlist"
                    update_playlist_entry(playlistJSON,1)


    with open("downloadLog.json", "w+") as output:
        json.dump(playlistJSON,output)


else:
    print "Can't get token for", username
