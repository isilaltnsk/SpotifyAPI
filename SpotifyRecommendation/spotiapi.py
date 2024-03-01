import pandas as pd
import requests
import base64
import spotipy
# import numpy as np
# from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
# from spotipy.oauth2 import SpotifyOAuth

client_id = "a84e04d5fc1c4b8c87c0ddb2da4621c7"
client_secret = "6675c330250143a193d4e2ea6ec47ef1"
client_credentials = f"{client_id}:{client_secret}"
print(client_credentials)
client_credentials_base64 = base64.b64encode(client_credentials.encode())
print(client_credentials_base64)


token_url = 'https://accounts.spotify.com/api/token'
headers = {"Authorization": f"basic {client_credentials_base64.decode()}"}
data = {"grant_type": "client_credentials"}
response = requests.post(token_url, data=data, headers=headers)

if response.status_code == 200:
    access_token = response.json()["access_token"]
    print("Access token obtained")
else:
    print("error obtaining access token")
    exit()


def get_playlist_data(playlist_id, access_token):
    sp = spotipy.Spotify(auth=access_token)
    # sp ne oluyor burada ?

    try:
        playlist_tracks = sp.playlist_items(playlist_id, fields="items(track(id,name,artists,album(id,name)))")
    except spotipy.SpotifyException as e:
        print("Error retrieving playlist tracks:", e)
        return None

    music_data = []
    for track_info in playlist_tracks["items"]:
        track = track_info["track"]
        track_name = track["name"]
        artists = ",".join([artist["name"] for artist in track["artists"]])
        album_name = track["album"]["name"]
        album_id = track["album"]["id"]
        track_id = track["id"]

        # get audio features
        audio = sp.audio_features(track_id)[0] if track_id != "Not Available" else None

        # get release date
        try:
            album_info = sp.album(album_id) if album_id != "Not Available" else None
            release_date = album_info["release_date"] if album_info else None
        except:
            print("Error retrieving album info:")
            release_date = None

        # get popularity

        try:
            track_info = sp.track(track_id) if track_id != "Not Available" else None
            popularity = track_info["popularity"] if track_info else None
        except:
            print("Error retrieving track info:")
            popularity = None

        # Add additional track information to the track data
        track_data = {
            'Track Name': track_name,
            'Artists': artists,
            'Album Name': album_name,
            'Album ID': album_id,
            'Track ID': track_id,
            'Popularity': popularity,
            'Release Date': release_date,
            'Duration (ms)': audio['duration_ms'] if audio else None,
            'Explicit': track_info.get('explicit', None),
            'External URLs': track_info.get('external_urls', {}).get('spotify', None),
            'Danceability': audio['danceability'] if audio else None,
            'Energy': audio['energy'] if audio else None,
            'Key': audio['key'] if audio else None,
            'Loudness': audio['loudness'] if audio else None,
            'Mode': audio['mode'] if audio else None,
            'Speechiness': audio['speechiness'] if audio else None,
            'Acousticness': audio['acousticness'] if audio else None,
            'Instrumentalness': audio['instrumentalness'] if audio else None,
            'Liveness': audio['liveness'] if audio else None,
            'Valence': audio['valence'] if audio else None,
            'Tempo': audio['tempo'] if audio else None,
            # Add more attributes as needed
        }

        music_data.append(track_data)

    df = pd.DataFrame(music_data)
    return df


playlist_id = "2S5puhsG9gpRn3Q6EFmtJ9"
music_df = get_playlist_data(playlist_id, access_token)
if music_df is not None:
    print(music_df)
else:
    print("Failed to retrieve playlist data. Check if the playlist identifier is correct.")
print(music_df.isnull().sum())
data = music_df



def calculate_weighted_popularity(release_date):
    # Convert the release date string to a datetime object
    release_date = datetime.strptime(release_date, "%Y-%m-%d")
    # Calculate the time span between release date and today's date
    time_span = datetime.now() - release_date
    # Calculate the weighted popularity score based on time span
    weight = 1 / (time_span.days + 1)
    return weight

# normalize the music features using min-max scaling


scaler = MinMaxScaler()
music_features = music_df[["Danceability", "Energy", "Key",
                           "Loudness", "Mode", "Speechiness",
                           "Acousticness", "Instrumentalness",
                           "Liveness", "Valence", "Tempo"]].values
music_features_scaled = scaler.fit_transform(music_features)
print(music_features_scaled)


# a function to get content-based recommendations based on music features
def content_based_recommendations(song_name, num_recommendations=5):

    if song_name not in music_df["Track Name"].values:
        print(f"'{song_name}' not found in the dataset. please enter a valid song name")
        return

    # get the index of the input song in music dataframe
    song_index = music_df[music_df["Track Name"] == song_name].index[0]
    # calculate the similarity scores based on music features (cosine similarity)
    similarity_scores = cosine_similarity([music_features_scaled[song_index]], music_features_scaled)
    # get the indices of most similar songs
    similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations+1]
    # get the indices of the most similar songs based on content-based filtering
    content_based_recommendations = music_df.iloc[similar_song_indices][
        ['Track Name', 'Artists', 'Album Name', 'Release Date', 'Popularity']]
    return content_based_recommendations

# a function to get hybrid recommendations based on weighted popularity


def hybrid_recommendations(song_name, num_recommendations=5, alpha = 0.5):
    if song_name not in music_df["Track Name"].values:
        print(f"'{song_name}' not found in the dataset. Please enter a valid song name")
        return

    # get content based recom.
    content_based_rec = content_based_recommendations(song_name, num_recommendations)

    # get the popularity score of the input song
    popularity_score = music_df.loc[music_df['Track Name'] == song_name, 'Popularity'].values[0]

    # calculate the wighted popularity score
    weighted_popularity_score = popularity_score * calculate_weighted_popularity(music_df.loc[music_df['Track Name']
                                                                                              == song_name, 'Release Date'].values[0])

    # combine content_based and popularity-based recom. based on weighted popularity
    hybrid_recommendations_df = content_based_rec.copy()
    hybrid_recommendations_df = pd.DataFrame([{
        "Track Name": song_name,
        "Artists": music_df.loc[music_df["Track Name"] == song_name, "Artists"].values[0],
        "Album Name": music_df.loc[music_df["Track Name"] == song_name, "Album Name"].values[0],
        "Release Date": music_df.loc[music_df["Track Name"] == song_name, "Release Date"].values[0],
        "Popularity": weighted_popularity_score
    }])

    # Concatenate content-based recommendations and the input song DataFrame
    hybrid_recommendations_df = pd.concat([content_based_rec, hybrid_recommendations_df], ignore_index=True)
    # sort the hybrid recom. based on weighted popularity score
    hybrid_recommendations_df = hybrid_recommendations_df.sort_values(by="Popularity", ascending=False)

    # remove the input song from the recom
    hybrid_recommendations_df = hybrid_recommendations_df[hybrid_recommendations_df["Track Name"] != song_name]

    return hybrid_recommendations_df



song_name = "Metalingus "
recommendations = hybrid_recommendations(song_name, num_recommendations=5)
print(f"Hybrid recommended songs for '{song_name}':")
print(recommendations)
