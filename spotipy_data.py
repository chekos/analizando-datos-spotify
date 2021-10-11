from os import curdir
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from rich import print
import sqlite3
import pandas as pd

# Make sure you set up SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET envs
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def get_track_info(query):
    search_result = sp.search(query, limit=1)

    track = search_result["tracks"]["items"][0]
    _track = {}

    _track["artists_ids"] = []
    for artist in track["artists"]:
        _track["artists_ids"].append(artist["id"])

    _track["spotify_url"] = track["external_urls"]["spotify"]
    _track["duration_ms"] = track["duration_ms"]
    _track["explicit"] = track["explicit"]
    _track["name"] = track["name"]
    _track["popularity"] = track["popularity"]
    _track["preview_url"] = track["preview_url"]
    _track["track_number"] = track["track_number"]
    _track["type"] = track["type"]
    _track["uri"] = track["uri"]
    _track['id'] = track['id']

    return _track


def get_artist_info(query):
    search_result = sp.search(query, limit=1, type="artist")
    artist = search_result["artists"]["items"][0]
    _artist = {}

    _artist["genres"] = []
    for genre in artist["genres"]:
        _artist["genres"].append(genre)

    _artist["spotify_url"] = artist["external_urls"]["spotify"]
    _artist["name"] = artist["name"]
    _artist["popularity"] = artist["popularity"]
    _artist["href"] = artist["href"]
    _artist["type"] = artist["type"]
    _artist["uri"] = artist["uri"]
    _artist["followers"] = artist["followers"]["total"]
    _artist["image_url"] = artist["images"][0]["url"]

    return _artist


def save_tracks_info():
    conn = sqlite3.connect("mi_spotify.db")
    cursor = conn.cursor()
    get_tracks_sql = """SELECT distinct artist_name || " - " || track_name as name FROM streaming_history;"""
    q_results = cursor.execute(get_tracks_sql).fetchall()
    conn.close()
    tracks_info_list = []
    for tup in q_results:
        search_q = tup[0]
        try:
            tracks_info_list.append(get_track_info(search_q))
        except:
            try:
                tracks_info_list.append(get_track_info(search_q.replace(" - ", " ")))
            except:
                print(f"{search_q.replace(' - ',' ')}")

    pd.DataFrame(tracks_info_list).to_csv(
        "csvs/tracks_info.csv", encoding="utf-8", index=False
    )


def save_artist_info():
    conn = sqlite3.connect("mi_spotify.db")
    cursor = conn.cursor()
    get_artists_sql = """SELECT distinct artist_name FROM streaming_history;"""
    q_results = cursor.execute(get_artists_sql).fetchall()
    conn.close()
    artist_info_list = []
    for tup in q_results:
        search_q = tup[0]
        try:
            artist_info_list.append(get_artist_info(search_q))
        except:
            try:
                artist_info_list.append(get_artist_info(search_q.replace(" - ", " ")))
            except:
                print(f"{search_q.replace(' - ',' ')}")

    pd.DataFrame(artist_info_list).to_csv(
        "csvs/artist_info.csv", encoding="utf-8", index=False
    )

def save_audio_features():
    conn = sqlite3.connect("mi_spotify.db")
    cursor = conn.cursor()
    get_tids_sql = """SELECT id FROM tracks_info;"""
    q_results = cursor.execute(get_tids_sql).fetchall()
    conn.close()
    tids = [tid[0] for tid in q_results]
    
    # max 100 per batch
    audio_features_list = []
    batch_size = 99
    for n in range(int(len(tids) / batch_size)+1):
        start = n * batch_size
        end = (n + 1) * batch_size
        print(f"getting tids: {start} - {end}")  
        for track in sp.audio_features(tids[start:end]):
            audio_features_list.append(track)

    audio_features_list = [item for item in audio_features_list if isinstance(item, dict)]
    pd.DataFrame(audio_features_list).to_csv("csvs/audio_features.csv", encoding='utf-8', index = False)

if __name__ == "__main__":
    # save_tracks_info()
    # save_artist_info()
    save_audio_features()
