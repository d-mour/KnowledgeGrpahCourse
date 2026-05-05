import os
import math
import time
import asyncio
import spotify
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
load_dotenv()


def stack_ids(ids):
    return ",".join(list(ids))


async def main():
    delay = 1
    batch_size = 20
    client_id = os.getenv("SPOTIFY_CLIEND_ID")
    secret = os.getenv("SPOTIFY_SECRET")

    client = spotify.Client(client_id, secret)
    df = pd.read_csv("data/albums.csv", usecols=["album_id", "performer_id"])
    album_ids = df["album_id"].to_numpy()

    albums = []
    pbar = tqdm(range(int(math.ceil(len(album_ids) / batch_size))))

    banned_keys = [
        "tracks", "artists", "external_urls", "available_markets",
        "href", "images", "uri", "type", "copyrights"
    ]

    for i in pbar:
        start = time.perf_counter()
        batch_ids = album_ids[i*batch_size:(i+1)*batch_size]
        albums_info = await client.http.albums(stack_ids(batch_ids))

        for album in albums_info["albums"]:
            album_info = {k: album[k] for k in set(album.keys()).difference(banned_keys)}
            albums.append(album_info)

        elapsed = time.perf_counter() - start
        time.sleep(max(delay - elapsed, 0))

    albums_full = pd.DataFrame(albums)
    albums_full["performer_id"] = df["performer_id"]
    albums_full.to_csv("data/albums_full.csv", index=False)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
