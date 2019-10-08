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
    client_id = "ee2b08265749477a8b156339bdfa0de5"
    client_secret = "bfb44ef7d7084c4ab78bbe25bb14eb47"
    redirect_uri = "http://localhost:3000/redirect"
    scope = 'playlist-read-private playlist-read-collaborative'

    def executeStates(gridIn):
        grid = gridIn
        def mainMenu(username, token):
            def updateUsers():
                users = None
                with open("users.json", "r") as input:
                    users = json.load(input)
                userJSONEntry = { username : "" }
                if userJSONEntry not in users['users']:
                    users['users'].append({
                        username : ""
                    })
                with open("users.json", "w+") as output:
                    users['latest'] = username
                    json.dump(users,output)

            def getToken():
                cache_path = ".cache-" + username
                sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope, cache_path=cache_path)
                token_info = sp_oauth.get_cached_token()
                token = token_info['access_token']
                return token

            def printPlaylists(playlists,playlistJSON):
                for playlist in playlists['items']:
                    print playlist['name']
                        #TODO: print playlist pic?
                        # print playlist['name'] - "  total tracks: " + str(playlist['tracks']['total'])

            clearGrid()
            grid.addWidget(QLabel("Select Playlists to Download"),0,0)
            updateUsers()

            if token == None:
                token = getToken()

            sp = spotipy.Spotify(token)
            # print sp.me()['id']
            playlists = sp.user_playlists(sp.me()['id'])

            if not path.exists("downloadLog.json"):
                open("downloadLog.json","w+")
            if os.stat("downloadLog.json").st_size != 0:
                with open("downloadLog.json", "r") as input:
                    playlistJSON = json.load(input)
            else:
                playlistJSON = {}



            printPlaylists(playlists,playlistJSON)

            #TODO: Show playlists such that they can be checked and unchecked
            #      "Download & Update button on the bottom right"
            #       Download & update page (No buttons allowed) & its redirection to the mainmenu page afterwards


        def clearGrid():
            for i in reversed(range(grid.count())):
                grid.itemAt(i).widget().setParent(None)

        def waitingSpotifyVerif(username):
            cache_path = None or ".cache-" + username
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
                with open("users.json", "r") as input:
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
            if os.path.exists('./users.json') and os.stat("users.json").st_size != 0:
                with open("users.json", "r") as input:
                    users = json.load(input)
                if not users == {}:
                    name = users['latest']

            else:
                with open("users.json", "w+") as output:
                    users = {"latest":"","users":[]}
                    json.dump(users,output)

            grid.addWidget(QLabel("Spotify Account Username:"),0,0)
            spotify_user = QLineEdit();
            spotify_user.setText(name)
            grid.addWidget(spotify_user,0,1);
            pybutton = QPushButton('Go!')
            pybutton.clicked.connect(clickMethod)
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
