import os
import uuid
import math
import time
import asyncio
import spotify
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
load_dotenv()


class Wrapper:
    def __init__(self, data: dict):
        self.data = data
    def __repr__(self) -> str:
        return f"{self.data['type']}: {self.data['name']}"
    def __hash__(self) -> int:
        return hash(self.data["id"])
    def __eq__(self, other: 'Wrapper'):
        return self.data["id"] == other.data["id"]
    

class Performer:
    def __init__(self, artists: list):
        self.artists = artists
        self.ids = frozenset([artist["id"] for artist in self.artists])
        self.uuid = uuid.uuid4()
    def get_row(self):
        return self.uuid, [artist["id"] for artist in self.artists]
    def __repr__(self) -> str:
        return f"artists: {list(self.ids)}"
    def __eq__(self, other: 'Performer') -> bool:
        return self.ids == other.ids
    def __hash__(self) -> int:
        return hash(self.ids)


def stack_track_ids(ids):
    return ",".join(list(ids))


async def main():
    client_id = os.getenv("SPOTIFY_CLIEND_ID")
    secret = os.getenv("SPOTIFY_SECRET")

    client = spotify.Client(client_id, secret)

    df = pd.read_csv("data/final_df.csv", usecols=["spotify_id"])
    df = df.drop_duplicates(subset=["spotify_id"]).reset_index(drop=True)
    print(f"Totat tracks: {len(df)}")

    delay = 1
    batch_size = 50
    spotify_ids = df["spotify_id"].to_numpy()

    tracks_set = set()
    albums_set = set()
    performers_set = set()

    pbar = tqdm(range(int(math.ceil(len(spotify_ids) / batch_size))))
    for i in pbar:
        start = time.perf_counter()
        batch_ids = spotify_ids[i*batch_size:(i+1)*batch_size]
        tracks_info = await client.http.tracks(stack_track_ids(batch_ids))

        for track in tracks_info["tracks"]:
            album = track["album"]
            track["album_id"] = album["id"]
            track_performer = Performer(track["artists"])
            album_performer = Performer(album["artists"])
            performers_set.add(track_performer)
            performers_set.add(album_performer)
            performers_keys = {p.ids: p for p in performers_set}
            track_performer_uuid = performers_keys[track_performer.ids].uuid
            album_performer_uuid = performers_keys[album_performer.ids].uuid
            track["performer_id"] = track_performer_uuid
            album["performer_id"] = album_performer_uuid
            albums_set.add(Wrapper(album))
            tracks_set.add(Wrapper(track))

            del album["artists"]
            del track["artists"]
            del track["album"]
        
        pbar.set_description(
            f"len(tracks) = {len(tracks_set)} len(performers) = {len(performers_set)}, len(albumns) = {len(albums_set)}"
        )

        elapsed = time.perf_counter() - start
        time.sleep(max(delay - elapsed, 0))
    
    
    tracks_data = pd.DataFrame([track.data for track in tracks_set])
    tracks_data.to_csv("data/tracks.csv", index=False)

    albums_data = pd.DataFrame([album.data for album in albums_set])
    albums_data.to_csv("data/albums.csv", index=False)

    performer_data = pd.DataFrame(
        [p.get_row() for p in performers_set],
        columns=['performer_id', 'artist_ids']
    )
    performer_data.to_csv("data/performers.csv", index=False)

    artists_set = set()
    for performer in performers_set:
        artists = map(Wrapper, performer.artists)
        artists_set.update(artists)
    
    artists_data = pd.DataFrame([artist.data for artist in artists_set])
    artists_data.to_csv("data/artists.csv", index=False)

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
