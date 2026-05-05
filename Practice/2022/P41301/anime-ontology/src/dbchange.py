import json
import requests
import time
from lxml import html
import warnings
from pymongo import MongoClient
import pymongo
from progress.bar import IncrementalBar

warnings.filterwarnings("ignore")
BASE_URL = 'https://shikimori.one/api'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'

session_wp = requests.Session()
session_wp.headers = {
    'User-Agent': user_agent
}

def get_shiki_anime(animeName): #return first searched anime by name
    search = get_shiki_response(f'/animes/search?q={animeName}')
    anime = get_shiki_response(f'/animes/{search[0]["id"]}')
    return anime

def get_shiki_response(path):
    r = session_wp.get(f'{BASE_URL}{path}')

    if r.status_code == 200:
        time.sleep(1)
        return json.loads(r.text)
    else:
        print('Error')
        time.sleep(4)
        return get_shiki_response(path)

def get_database():
    
    CONNECTION_STRING = "mongodb://root:pass12345@localhost:27017/"

    client = MongoClient(CONNECTION_STRING)

    return client['AniDb']

def json_replace(json):
    try:
        temp = {}
        temp2 = {}
        new_anime = {}
        for k in json.keys():
            if k != 'info':
                temp.update({k: json[k]}) 
        for i in json['info']['anime']:
            new_anime.update(i)
        temp2.update({'anime': new_anime})
        temp2.update({'relations': json['info']['relations']})
        temp2.update({'characteristics': keys_to_lower(json['info']['characteristics'])})
        temp.update({'info':temp2})
        return temp
    except:
        return json

def keys_to_lower(dict):
    temp = {}
    for k in dict.keys():
        temp.update({k.lower():dict[k]})
    return temp

def change_in_db():
    db = get_database()
    items = db['Characters'].find()
    total_count =  db['Characters'].count_documents({})
    bar = IncrementalBar('Characters', max = total_count)
    for item in items:
        db['Characters'].replace_one({'_id':item['_id']}, json_replace(item))
    bar.finish()

def save_to_json(json_name):
    db = get_database()
    array = []
    items = db['Characters'].find()
    total_count =  db['Characters'].count_documents({})
    bar = IncrementalBar('Characters', max = total_count)
    js = list(items)
    for item in js:
        #db['Characters'].replace_one({'_id':item['_id']}, json_replace(item))
        item.pop("_id")
        array.append(item)
        bar.next()
        
    with open(json_name, 'w+', encoding='utf-8') as file:
        json.dump(array,file,ensure_ascii=False)
        file.close()
    bar.finish()
def main():
    #change_in_db()
    save_to_json('jsons/processed/data_json.json')

if __name__ == '__main__':
    main()