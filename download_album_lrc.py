## https://www.deezer.com/nl/album/455478955

import deezer
import sys
from halo import Halo
import os, time, requests, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service

def get_track_lyrics(id, token):
    data = {}
    data["operationName"] = "SynchronizedTrackLyrics"
    data["query"] = "query SynchronizedTrackLyrics($trackId: String!) {  track(trackId: $trackId) {    ...SynchronizedTrackLyrics    __typename  }}fragment SynchronizedTrackLyrics on Track {  id  lyrics {    ...Lyrics    __typename  }  album {    cover {      small: urls(pictureRequest: {width: 100, height: 100})      medium: urls(pictureRequest: {width: 264, height: 264})      large: urls(pictureRequest: {width: 800, height: 800})      explicitStatus      __typename    }    __typename  }  __typename}fragment Lyrics on Lyrics {  id  copyright  text  writers  synchronizedLines {    ...LyricsSynchronizedLines    __typename  }  __typename}fragment LyricsSynchronizedLines on LyricsSynchronizedLine {  lrcTimestamp  line  lineTranslated  milliseconds  duration  __typename}"
    data["variables"] = {"trackId": str(id)}

    headers = {}
    headers["Authorization"] = token
    headers["Content-Type"] = "application/json"

    resp = requests.post("https://pipe.deezer.com/api", data=json.dumps(data), headers=headers)

    if resp.status_code > 400:
        print(resp.text)
        exit(0)

    return resp.text

album_id = int(sys.argv[1])
print("Getting album with ID " + str(album_id))

client = deezer.Client()
album = client.get_album(album_id)
print("'" + album.title + "' by '" + album.artist.name + "'")

print("\n --- TRACKLIST ---")
for i in album.tracks:
    print("'" + i.title + "'" + " - ID " + str(i.id))
print("\n")
    
token = input("Enter bearer token: ")


print("\n --- DOWNLOADING ---")
for i in album.tracks:
    with Halo(text=i.title, spinner="simpleDotsScrolling"):
        data = json.loads(get_track_lyrics(i.id, token))
        parsed = data["data"]["track"]
        parsed["title"] = i.title
        parsed["album_title"] = i.album.title
        parsed["artist"] = i.artist.name

        try:
            with open("./downloaded/" + str(i.id) + ".dlrc", "w") as file:
                file.write(json.dumps(parsed))
        except:
            print("ERROR: '" + i.title + "' has failed!")

print("All tracks finished!")

def get_token():
    print("Starting browser to get a token")
    opts = webdriver.ChromeOptions()
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    browser = webdriver.Chrome(service=Service("/usr/lib/chromium-browser/chromedriver"), options=opts)
    browser.get("https://www.deezer.com/nl/album/455478955")

    buttons = browser.find_element(By.XPATH, "//button[@aria-label='Afspelen met lyrics')]")
    buttons[0].click()

    logs = browser.get_log("performance")
    for entry in logs:
        if "Bearer" in str(entry["message"]):
            token = (entry["message"].split()[3]).split('"')[0]

            print(entry["message"])
            print(token)

    exit(1)
