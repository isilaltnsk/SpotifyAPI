import requests
import base64
import panda
import spotipy
from spotipy.oauth2 import SpotifyOAuth

client_id = "a84e04d5fc1c4b8c87c0ddb2da4621c7"
client_secret = "6675c330250143a193d4e2ea6ec47ef1"
client_credentials = f"{client_id}:{client_secret}"
print(client_credentials)
client_credentials_base64 = base64.b64encode(client_credentials.encode())

token_url = 'https://accounts.spotify.com/api/token'
headers = {"Authorization": f"basic {client_credentials_base64.decode()}"}
data = {"grant_type":"client_credentials"}
response = requests.post(token_url, data=data, headers=headers)

if response.status_code == 200:
    access_token = response.json()["access_token"]
    print("Access token obtained")
else:
    print("error obtaining access token")
    exit()


def get_playlist_data(playlist_id, token):
    sp = spotipy.Spotify(auth=token)

    playlist_tracks = sp.playlist_tracks(playlist_id, fields="items(track(id,name,artists,album(id,name)))")

    music_data = []
    for track_info in playlist_tracks["items"]:
        track = track_info["track"]
        track_name = track["name"]
        artists = ",".join([artist["name"] for artist in track ["artists"]])
        album_name = track["album"]["name"]
        album_id = track["album"]["id"]
        track_id = track["id"]

        #get audio features
        audio = sp.audio_features(track_id)[0] if track_id != "Not Available" else None

        #get release date
        try:
            album_info = sp.album(album_id) if album_id != "Not Available" else None

            release_date = album_info["release_date"] if album_info else None

        except:
            release_date = None


        #get popularity

