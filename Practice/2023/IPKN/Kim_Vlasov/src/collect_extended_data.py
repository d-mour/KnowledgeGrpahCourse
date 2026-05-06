import pandas as pd
import musicbrainzngs
from tqdm import tqdm
from collections import defaultdict


def safe_get_value(data_dict, path):
    try:
        for key in path:
            data_dict = data_dict[key]
        return data_dict
    except (KeyError, TypeError):
        return None


def main():
    start = 0
    end = 1500
    df = pd.read_csv("data/final_df.csv")
    df = df.drop_duplicates(subset=["artist"]).reset_index(drop=True)
    df = df.iloc[start:end]
    track_names = df["name"].to_numpy()
    performer_names = df["artist"].to_numpy()
    performer_ids = df['spotify_id'].to_numpy()

    artists_data = defaultdict(list)
    events_data = defaultdict(list)

    for track, performer, id in tqdm(zip(track_names, performer_names, performer_ids)):
        res = musicbrainzngs.search_recordings(artist=performer, recording=track)
        performer_id = res['recording-list'][0]['artist-credit'][0]['artist']['id']

        events_info = musicbrainzngs.browse_events(artist=performer_id, includes=['place-rels'])
        for event in events_info['event-list']: 
            event_adress = safe_get_value(event, ['place-relation-list', 0, 'place'])
            events_data['performer_id'].append(id)
            events_data['name'].append(safe_get_value(event, ['name']))
            events_data['start_date'].append(safe_get_value(event, ['life-span', 'begin']))
            events_data['end_date'].append(safe_get_value(event, ['life-span', 'end']))
            events_data['adress'].append(safe_get_value(event_adress, ['adress']))
            events_data['longitude'].append(safe_get_value(event_adress, ['coordinates', 'longitude']))
            events_data['latitude'].append(safe_get_value(event_adress, ['coordinates', 'latitude']))

        performer_info = musicbrainzngs.get_artist_by_id(performer_id, includes=['artist-rels'])
        performer_info = performer_info['artist']
        if 'artist-relation-list' in performer_info:
            for artist in performer_info['artist-relation-list']:
                artists_data['performer_id'].append(id)
                artists_data['performer_country'].append(safe_get_value(performer_info, ['country']))
                artists_data['start_date_performer'].append(safe_get_value(performer_info, ['life-span', 'begin']))
                artists_data['end_date_performer'].append(safe_get_value(performer_info, ['life-span', 'end']))
                artist_id = artist['artist']['id']
                artists_data['name'].append(safe_get_value(artist, ['artist', 'name']))
                artists_data['start_date_artist'].append(safe_get_value(artist, ['begin']))
                artists_data['end_date_artist'].append(safe_get_value(artist, ['end']))
                artists_data['instrument'].append(safe_get_value(artist, ['attribute-list']))
                artist_info = musicbrainzngs.get_artist_by_id(artist_id, includes=['artist-rels'])
                artist_info = artist_info['artist']
                artists_data['artist_country'].append(safe_get_value(artist_info, ['country']))
                artists_data['gender'].append(safe_get_value(artist_info, ['gender']))
                artists_data['age'].append(safe_get_value(artist_info, ['life-span', 'begin']))
                artists_data['death_date'].append(safe_get_value(artist_info, ['life-span', 'end']))
    
    events_data = pd.DataFrame(events_data)
    events_data.to_csv(f"data/events_data_{start}_{end}.csv", index=False)
    artists_data = pd.DataFrame(artists_data)
    artists_data.to_csv(f"data/artists_data_{start}_{end}.csv", index=False)


if __name__ == "__main__":
    musicbrainzngs.set_useragent(
        "MusicOntology",
        "0.1",
        "https://github.com/sesevasa64/MusicOntology/",
    )
    musicbrainzngs.set_rate_limit(limit_or_interval=1.0)
    main()