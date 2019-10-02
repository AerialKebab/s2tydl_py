import sys
import spotipy
import spotipy.util as util
import os
from selenium import webdriver
from spotipy import oauth2

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



client_id = "4eacb90864a74bc49e17a90d591723d7"
client_secret = "f22221c21ede49e989f67e69ff5d4db6"
redirect_uri = "http://localhost:3000/redirect"
scope = 'user-library-read'


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

# token = prompt_for_user_token(username, scope)


if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print track['name'] + ' - ' + track['artists'][0]['name']
else:
    print "Can't get token for", username
