import csv
import datetime
import json
import os
import re

import requests
from yandex_music import Client
from yandex_music.exceptions import NotFoundError

with open('auth.json', 'r') as fp:
    TOKEN = json.load(fp)["yandex_token"]

client = Client(TOKEN).init()

type_to_name = {
    'track': 'трек',
    'artist': 'исполнитель',
    'album': 'альбом',
    'playlist': 'плейлист',
    'video': 'видео',
    'user': 'пользователь',
    'podcast': 'подкаст',
    'podcast_episode': 'эпизод подкаста',
}


def search_playlists(query: str, fetch_tracks: bool = False, limit: int = 10):
    search_result = client.search(query).playlists
    results = []
    if "yandex.csv" not in os.listdir():
        writer = csv.writer(open("yandex.csv", "w", newline="", encoding="utf-8"))
        writer.writerow(["id", "title", "artists", "album", "album_id", "time", "playlist", "lyrics", "query", "path"])
    writer = csv.writer(open("yandex.csv", "a+", newline="", encoding="utf-8"))

    count = 0
    for result in search_result.results:
        playlist = result.fetch_tracks()
        # create a dir for each playlist

        if fetch_tracks:
            playlist_dir = f"playlists/{result.title}"
            try:
                os.makedirs(playlist_dir)
            except FileExistsError:
                pass
        for track_short in playlist:
            if count >= limit:
                return results

            track = track_short.track
            artists = track.artists
            album = track.albums[0]
            try:
                lyrics_info = track.get_lyrics()
                lyrics = requests.get(lyrics_info["download_url"]).text
            except NotFoundError:
                lyrics = None

            info = {
                "id": track.id,
                "title": re.sub(r'[^\w\s]', '', track.title),
                "artists": ', '.join(artist.name for artist in artists),
                "album": album.title,
                "album_id": album.id,
                "time": datetime.datetime.now(),
                "playlist": re.sub(r'[^\w\s]', '', result.title),
                "lyrics": lyrics,
                "query": query,
                "path": f"{playlist_dir}/{track.title}.mp3" if fetch_tracks else None
            }
            if fetch_tracks:
                fetched_track = track_short.fetch_track()
                try:
                    fetched_track.download(f"{playlist_dir}/{track.title}.mp3")
                except Exception as e:
                    print(e)
                    continue
            writer.writerow(list(info.values()))
            results.append(info)
            count += 1

    return results


if __name__ == '__main__':
    genres = ["rock", "pop", "rap", "jazz", "blues", "metal", "classical", "electronic", "hip-hop", "indie", "folk"]
    for genre in genres:
        search_playlists(genre, limit=100, fetch_tracks=False)
