import pandas as pd
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF, XSD
from tqdm import tqdm


def main():
    # Create an emprty graph
    g = Graph()
    g.parse("data/music_ontology.owl")

    # Loop through each triple in the graph (subj, pred, obj)
    for subj, pred, obj in g:
        # Check if there is at least one triple in the Graph
        if (subj, pred, obj) not in g:
            raise Exception("It better be!")

    # Print the number of "triples" in the Graph
    print(f"Graph g has {len(g)} statements.")

    base_url = "http://www.semanticweb.org/music-ontology"

    name_dp = URIRef(f"{base_url}#name")
    label_dp = URIRef(f"{base_url}#label")
    albumType_dp = URIRef(f"{base_url}#albumType")
    tracksTotal_dp = URIRef(f"{base_url}#tracksTotal")
    releaseYear_dp = URIRef(f"{base_url}#releaseYear")
    instrument_dp = URIRef(f"{base_url}#instrument")
    country_dp = URIRef(f"{base_url}#country")
    gender_dp = URIRef(f"{base_url}#gender")
    age_dp = URIRef(f"{base_url}#age")

    startDate_dp = URIRef(f"{base_url}#startDate")
    endDate_dp = URIRef(f"{base_url}#endDate")
    
    longitude_dp = URIRef(f"{base_url}#longitude")
    latitude_dp = URIRef(f"{base_url}#latitude")
    adress_dp = URIRef(f"{base_url}#adress")

    # Classes
    Track_class, Performer_class, Artist_class, Genre_class, Album_class, Event_class = \
        [URIRef(f"{base_url}#{c}") for c in ["Track", "Performer", "Artist", "Genre", "Album", "Event"]]

    # Object properties
    hasAssociatedGenre_op, hasGenre_op, includedIn_op, participatedIn_op, partOf_op, performedBy_op = \
        [URIRef(f"{base_url}#{op}") for op in ["hasAssociatedGenre", "hasGenre", "includedIn", "participatedIn", "partOf", "performedBy"]]

    # Data properties
    dp_names = [
        "acousticness", "country", "danceability", "performedBy", "duration", "energy", "instrumentalness",
        "label", "liveness", "loudness", "name", "popularity", "releaseYear", "speechiness", "tempo", "valence"
    ]

    df = pd.read_csv("data/final_df.csv")
    albums = pd.read_csv("data/albums_full_correct.csv")
    artist = pd.read_csv("data/artist_data_correct.csv")
    tracks = pd.read_csv("data/tracks_correct.csv")
    events = pd.read_csv("data/events_data_correct.csv")

    df.drop_duplicates(subset=['spotify_id'], inplace=True)
    data = df.merge(tracks, how='inner', left_on='spotify_id', right_on='id')
    data['genre'] = data['genre'].replace(' ', '_', regex=True)

    df_mapping = {
        "name": "name_x",
        "duration": "duration_ms_x",
        "performedBy": "performer_id",
        "releaseYear": "year",
    }

    performers = artist.drop_duplicates(subset="performer_id")
    for idx, row in tqdm(performers.iterrows(), total=len(performers)):
        performer_individual = URIRef(f"{base_url}#performer_{row['performer_id']}")
        g.add((performer_individual, RDF.type, Performer_class))
        g.add((performer_individual, name_dp, Literal(row["performer_name"])))
        if not pd.isna(row["performer_country"]):
            g.add((performer_individual, country_dp, Literal(row["performer_country"])))
        if not pd.isna(row["start_date_performer"]):
            g.add((performer_individual, startDate_dp, Literal(row["start_date_performer"])))
        if not pd.isna(row["end_date_performer"]):
            g.add((performer_individual, endDate_dp, Literal(row["end_date_performer"])))

    artist_sub = artist.drop_duplicates(subset=["name", "age"])
    for idx, row in tqdm(artist_sub.iterrows(), total=len(artist_sub)):
        performer_individual = URIRef(f"{base_url}#performer_{row['performer_id']}")
        artist_individual = URIRef(f"{base_url}#artist_{idx}")
        g.add((artist_individual, RDF.type, Artist_class))
        g.add((artist_individual, name_dp, Literal(row["name"])))
        if not pd.isna(row["age"]):
            g.add((artist_individual, age_dp, Literal(row["age"])))
        if not pd.isna(row["artist_country"]):
            g.add((artist_individual, country_dp, Literal(row["artist_country"])))
        if not pd.isna(row["gender"]):
            g.add((artist_individual, gender_dp, Literal(row["gender"])))
        if not pd.isna(row["start_date_artist"]):
            g.add((artist_individual, startDate_dp, Literal(row["start_date_artist"])))
        if not pd.isna(row["end_date_artist"]):
            g.add((artist_individual, endDate_dp, Literal(row["end_date_artist"])))
        if not pd.isna(row["instrument"]):
            g.add((artist_individual, instrument_dp, Literal(row["instrument"][0])))
        g.add((artist_individual, includedIn_op, performer_individual))

    for idx, row in tqdm(albums.iterrows(), total=len(albums)):
        album_individual = URIRef(f"{base_url}#album_{row['id']}")
        performer_individual = URIRef(f"{base_url}#performer_{row['performer_id']}")
        g.add((album_individual, RDF.type, Album_class))
        if not pd.isna(row['name']):
            g.add((album_individual, name_dp, Literal(row['name'])))
        g.add((album_individual, tracksTotal_dp, Literal(row['total_tracks'])))
        if not pd.isna(row['label']):
            g.add((album_individual, label_dp, Literal(row['label'])))
        g.add((album_individual, performedBy_op, performer_individual))
        g.add((album_individual, albumType_dp, Literal(row["album_type"])))
        if row["release_date_precision"] == "year":
            g.add((album_individual, releaseYear_dp, Literal(row['release_date'])))

    event_props = ["adress", "longitude", "latitude", "start_date", "end_date"]
    for idx, row in tqdm(events.iterrows(), total=len(events)):
        adress, longitude, latitude, start_date, end_date = [row[prop] for prop in event_props]
        event_individual = URIRef(f"{base_url}#event_{idx}")
        performer_individual = URIRef(f"{base_url}#performer_{row['performer_id']}")
        g.add((event_individual, RDF.type, Event_class))
        g.add((event_individual, name_dp, Literal(row["name"])))
        if not pd.isna(adress):
            g.add((event_individual, adress_dp, Literal(adress)))
        if not pd.isna(longitude):
            g.add((event_individual, longitude_dp, Literal(longitude)))
        if not pd.isna(latitude):
            g.add((event_individual, latitude_dp, Literal(latitude)))
        if not pd.isna(start_date):
            g.add((event_individual, startDate_dp, Literal(start_date, datatype=XSD.date)))
        if not pd.isna(end_date):
            g.add((event_individual, endDate_dp, Literal(end_date, datatype=XSD.date)))
        g.add((performer_individual, participatedIn_op, event_individual))

    for genre in data["genre"].dropna().unique():
        genre_individual = URIRef(f"{base_url}#genre_{genre}")
        g.add((genre_individual, RDF.type, Genre_class))
        g.add((genre_individual, name_dp, Literal(genre)))

    for index, row in tqdm(data.iterrows(), total=len(data)):
        track_individual = URIRef(f"{base_url}#track_"+row['spotify_id'])
        g.add((track_individual, RDF.type, Track_class))

        performer_individual = URIRef(f"{base_url}#performer_{row['performer_id']}")
        album_individual = URIRef(f"{base_url}#album_{row['album_id']}")
        if not pd.isna(row['genre']):
            genre_individual = URIRef(f"{base_url}#genre_{row['genre']}")

        # g.add((performer_individual, hasAssociatedGenre_op, genre_individual))
        g.add((track_individual, hasGenre_op, genre_individual))
        g.add((track_individual, partOf_op, album_individual))
        g.add((track_individual, performedBy_op, performer_individual))

        for dp_name in dp_names:
            if dp_name in ["country", "label"]:
                continue

            track_dp = URIRef(f"{base_url}#{dp_name}")

            df_name = dp_name
            if df_name not in data.columns:
                df_name = df_mapping[dp_name]

            g.add((track_individual, track_dp, Literal(row[df_name])))

    g.serialize("data/music_graph.ttl")
    g.close()


if __name__ == "__main__":
    main()
