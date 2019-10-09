from __future__ import unicode_literals
import sys
import spotipy
import spotipy.util as util
import os
from os import path
from selenium import webdriver
from spotipy import oauth2
import json, operator

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import urllib
import urlparse
from bs4 import BeautifulSoup

import youtube_dl

from pydub import AudioSegment

from multiprocessing import Pool, Process


#section modified from: https://github.com/plamere/spotipy/blob/master/spotipy/util.py#L18
#and https://github.com/plamere/spotipy/blob/master/spotipy/oauth2.py

def window():
    client_id = "4eacb90864a74bc49e17a90d591723d7"
    client_secret = "f22221c21ede49e989f67e69ff5d4db6"
    redirect_uri = "http://localhost:3000/redirect"
    scope = 'playlist-read-private playlist-read-collaborative'
    playlistJSON = None;

    def executeStates(gridIn):
        grid = gridIn
        def mainMenu(username, token):
            def updateUsers():
                users = None
                with open("./caches/users.json", "r") as input:
                    users = json.load(input)
                userJSONEntry = { username : "" }
                if userJSONEntry not in users['users']:
                    users['users'].append({
                        username : ""
                    })
                with open("./caches/users.json", "w+") as output:
                    users['latest'] = username
                    json.dump(users,output)

            def getToken():
                cache_path = "./caches/.cache-" + username
                sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope, cache_path=cache_path)
                token_info = sp_oauth.get_cached_token()
                token = token_info['access_token']
                return token

            def getPlaylists(playlists):
                playlistForm = QFormLayout()
                scrollPlaylists = QtWidgets.QScrollArea()
                groupBox = QGroupBox("Playlists")
                # buttonList = []
                for playlist in playlists['items']:
                    if playlist['name'] not in playlistJSON:
                        #TODO: fix playlist name repeats, input (3) change to ID?
                        playlistJSON[playlist['name']] = []
                        playlistJSON[playlist['name']].append({
                            'toDownload':0,
                            'numOfSongs':playlist['tracks']['total'],
                            'lastUpdated':0,
                            'songs': []
                        })
                    playlistJSON[playlist['name']][0]['numOfSongs'] = playlist['tracks']['total']
                    #TODO: New songs added

                    toDownload = QCheckBox()
                    if playlistJSON[playlist['name']][0]['toDownload'] == 1:
                        toDownload.setChecked(True)

                    playlistForm.addRow(toDownload,QLabel(playlist['name']))

                groupBox.setLayout(playlistForm)
                scrollPlaylists.setWidget(groupBox)
                scrollPlaylists.setWidgetResizable(True)
                grid.addWidget(scrollPlaylists,1,0)

                # https://doc.qt.io/qt-5/qformlayout.html

                dl = QPushButton('Download Playlists')
                dl.clicked.connect(downloadPlaylists)
                grid.addWidget(dl,2,0)

            def downloadPlaylists():
                # print grid.itemAtPosition(1,0).widget().widget().layout().rowCount()
                #QScrollArea/QGroupBox/QFormLayout (QFormLayout has rows)
                #TODO Downloading screen

                playlistRows = grid.itemAtPosition(1,0).widget().widget().layout()

                for i in range(playlistRows.rowCount()):
                    row = playlistRows.itemAt(i,0).widget()
                    playlistName = playlistRows.itemAt(i,1).widget().text()
                    if row.isChecked():
                        playlistJSON[playlistName][0]['toDownload'] = 1
                        # updatePlaylistEntry(playlistName) #TODO
                    else:
                        playlistJSON[playlistName][0]['toDownload'] = 0

                with open("./downloadLogs/" + username + "downloadLog.json", "w+") as output:
                    json.dump(playlistJSON,output)

            # def updatePlaylistEntry(playlistName):
            #     def insert_tracks_newPlaylist(tracks, songList):
            #         for i, item in enumerate(tracks['items']):
            #             track = item['track']
            #
            #             # print item['added_at']
            #
            #             songList.append({
            #                 track['id']: track['artists'][0]['name'] + " - " + track['name'],
            #                 'added_at': item['added_at']
            #             })
            #
            #             trackName = track['artists'][0]['name'] + " - " + track['name']
            #             # print trackName
            #             downloadVideo(findFirstYouTubeResult(track['artists'][0]['name'] + " - " + track['name']), trackName)
            #
            #     def insert_new_tracks(tracks, songList):
            #         for i, item in enumerate(tracks['items']):
            #             if item['added_at'] > playlistJSON[playlist['name']][0]['lastUpdated'] : ###
            #                 track = item['track']
            #                 songList.append({
            #                     track['id']: track['artists'][0]['name'] + " - " + track['name'],
            #                     'added_at': item['added_at']
            #                 })
            #                 playlistJSON[playlist['name']][0]['lastUpdated'] = item['added_at'];
            #                 trackName = track['artists'][0]['name'] + " - " + track['name']
            #                 print trackName
            #
            #                 downloadVideo(findFirstYouTubeResult(track['artists'][0]['name'] + " - " + track['name'] + "(Official Audio)"), trackName)
            #
            #     songList = []
            #     results = sp.user_playlist(username, playlist['id'],fields="tracks,next")
            #     tracks = results['tracks']
            #
            #     insert_tracks_newPlaylist(tracks,songList)
            #     while tracks['next']:
            #         tracks = sp.next(tracks)
            #         insert_tracks_newPlaylist(tracks,songList)
            #
            #     songList.sort(key=operator.itemgetter('added_at'))
            #     playlistJSON[playlistName]['songs'] = songList
            #
            #     # TODO
            #     # if playlist['tracks']['total'] != 0:
            #     #     playlistJSON[playlist['name']][0]['lastUpdated'] = playlistJSON[playlist['name']][1]['songs'][playlist['tracks']['total'] - 1]['added_at'] #lastelement

            clearGrid()
            grid.addWidget(QLabel("Select Playlists to Download"),0,0)
            updateUsers()

            if token == None:
                token = getToken()

            sp = spotipy.Spotify(token)
            playlists = sp.user_playlists(sp.me()['id'])

            if not path.exists("./downloadLogs/" + username + "downloadLog.json"):
                open("./downloadLogs/" + username + "downloadLog.json","w+")
            if os.stat("./downloadLogs/" + username + "downloadLog.json").st_size != 0:
                with open("./downloadLogs/" + username + "downloadLog.json", "r") as input:
                    playlistJSON = json.load(input)
            else:
                playlistJSON = {}

            getPlaylists(playlists)

        def clearGrid():
            for i in reversed(range(grid.count())):
                grid.itemAt(i).widget().setParent(None)

        def waitingSpotifyVerif(username):
            cache_path = None or "./caches/.cache-" + username
            sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope, cache_path=cache_path)
            token_info = sp_oauth.get_cached_token()

            if not token_info:
                driver = webdriver.Chrome(executable_path='./chromedriver/chromedriver')
                driver.get(sp_oauth.get_authorize_url())

                while driver.title != "localhost":
                    continue;

                # print driver.current_url

                token = sp_oauth.get_access_token(sp_oauth.parse_response_code(driver.current_url))['access_token']

                # credentials = oauth2.SpotifyClientCredentials(client_id=client_id,client_secret=client_secret)
                # token = credentials.get_access_token()


                driver.close()
            if token_info:
                token = token_info['access_token']
            if token:
                mainMenu(username, token)
            else:
                clearGrid()
                grid.addWidget(QLabel("Can't get token for " + username + ". Start Over?"),3,3)

        def enterSpotifyAcc():
            def goToSpotify():
                waitingSpotifyVerif(spotify_user.text())

            def clickMethod():
                clearGrid()

                users = None
                with open("./caches/users.json", "r") as input:
                    users = json.load(input)
                userJSONEntry = { spotify_user.text() : "" }

                if userJSONEntry in users['users']:
                    mainMenu(spotify_user.text(), None)
                else:
                    grid.addWidget(QLabel("Grant s2ytdl permissions from Spotify to add playlists"),0,0)
                    goto = QPushButton('Log into Spotify')
                    goto.clicked.connect(goToSpotify)
                    grid.addWidget(goto,0,2)

            name = None
            #if no file named lastUser do not fill in the entry text
            if os.path.exists('./caches/users.json') and os.stat("./caches/users.json").st_size != 0:
                with open("./caches/users.json", "r") as input:
                    users = json.load(input)
                if not users == {}:
                    name = users['latest']

            else:
                with open("./caches/users.json", "w+") as output:
                    users = {"latest":"","users":[]}
                    json.dump(users,output)

            grid.addWidget(QLabel("Spotify Account Username:"),0,0)
            spotify_user = QLineEdit();
            spotify_user.setText(name)
            grid.addWidget(spotify_user,0,1);
            pybutton = QPushButton('Go!')
            pybutton.clicked.connect(clickMethod)
            #TODO: Show playlists such that they can be checked and unchecked
            #      "Download & Update button on the bottom right"
            #       Download & update page (No buttons allowed) & its redirection to the mainmenu page afterwardsMethod)
            grid.addWidget(pybutton,0,2)

        enterSpotifyAcc()

    def center():
        frameGm = win.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        win.move(frameGm.topLeft())

    app = QApplication(sys.argv)
    win = QWidget()
    grid = QGridLayout()


    executeStates(grid)




    win.setLayout(grid)
    win.setWindowTitle("S2YTDL - by AerialKebab")
    win.setGeometry(50,50,200,200)
    win.show()
    win.setMinimumSize(500, 400);
    center()
    sys.exit(app.exec_())

if __name__ == '__main__':
   window()
