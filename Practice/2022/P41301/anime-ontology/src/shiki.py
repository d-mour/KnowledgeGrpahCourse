import requests

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'

headers = {
    'User-Agent': user_agent
}

_1 = 'https://shikimori.one/api/animes/48583'

anime_json = requests.get(_1, headers=headers).text

with open("jsons/raw/shiki_anime_raw.json", "w") as aniout:
    aniout.write(anime_json)
