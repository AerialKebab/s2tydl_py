Personal project created by Vergil Hsu

## Project objectives
I play with a DJ Controller as a hobby, mixing music for fun. (SoundCloud plug, listen to me!: https://soundcloud.com/aerialkebab). In order to mix, I need the files actually sitting in my hard drive. Obtaining music to mix can sometimes be a hassle, as I get my new music mainly through Spotify, and put it in a Spotify playlist. I then later look at the playlist when I have time, then download the files one by one. I thought of creating a project, that would be a desktop executable that would follow Spotify playlists, search those song names on YouTube, then download the first result from YouTube.

### Technologies used
* Spotipy - https://github.com/plamere/spotipy
* Google API Client Library for Python - https://developers.google.com/youtube/v3/quickstart/python
* youtube-dl: https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278
* py2exe - https://stackoverflow.com/questions/5458048/how-to-make-a-python-script-standalone-executable-to-run-without-any-dependency
* Selenium
* ffmpeg


## Future additions
Unfortunately searching YouTube directly through the song name supplied by the "song name + (audio)" can sometimes prove faulty. I want to implement a system that allows users to open up the original YouTube search, scroll through the results (within the UI) and select the right song from that. In the far future I would possibly create a database through these selection amounts on each video, and download the optimal video from that result.
