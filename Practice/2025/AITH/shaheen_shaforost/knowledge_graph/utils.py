import re

import pandas as pd


def clean_string_for_graph(string: str) -> str:
    return re.sub(r'[^\w\s]', '', string.lower().strip()).replace(" ", "_")


def get_artist_genre_set(df):
    artist_genre_set = {}
    for _, row in df.iterrows():
        artist = clean_string_for_graph(row["artist"])
        genre = clean_string_for_graph(row["genre"])
        if artist not in artist_genre_set:
            artist_genre_set[artist] = set()
        artist_genre_set[artist].add(genre)
    artists_dict = {"artist": [], "genre": []}
    for artist, genres in artist_genre_set.items():
        for genre in genres:
            artists_dict["artist"].append(artist)
            artists_dict["genre"].append(genre)

    artist_df = pd.DataFrame(artists_dict)

    return artist_df
