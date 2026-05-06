import json
import requests
import time
from lxml import html
import warnings
from pymongo import MongoClient
from progress.bar import IncrementalBar

warnings.filterwarnings("ignore")

BASE_URL = "https://anidb.net/ch"

BASE_URL_SHIKI = 'https://shikimori.one/api'

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'

session = requests.Session()
session_wp = requests.Session()
session.headers = {
    'User-Agent': user_agent
}
session_wp.headers = {
    'User-Agent': user_agent
}
#session.proxies = {}
proxies = []
session.verify = False
iter_proxy = iter(proxies)

def get_proxies():
    global proxies
    global iter_proxy
    with open("src/proxy_exports5.txt", 'r', encoding='utf-8') as proxy_file:
       string = proxy_file.readlines()
       for sub in string:
           s = sub.split()[0]
           proxies.append(s)
       iter_proxy = iter(proxies)
       proxy_file.close()

def change_proxy():
    global session
    # session = requests.Session()
    # session.headers = {
    # 'User-Agent': user_agent
    # }
    # session.verify = False
    # proxy = dict(https = f'socks5://{next(iter_proxy)}')
    # print(f'Changing proxy to {proxy}')
    # session.proxies = proxy
    # print('')
    
def get_tree_by_charcterId(id): #return html tree character's page on AniDb
    try:
        text = session.get(BASE_URL + str(id)).text
        return html.fromstring(text)
    except Exception as e:
        print(f'Error while get anidb tree... {e}')
        change_proxy()
        return get_tree_by_charcterId(id)

def parse_ani_db_page(id): #return main character info with anime ling on shiki in JSON
    try:
        tree = get_tree_by_charcterId(id)
        main_info = tree.xpath('//div[@id = "tab_1_pane"]//tbody//tr')
        animes = tree.xpath(f'//table[@id = "animelist_{id}"]/tbody/tr/td[@class = "name anime"]/a/text()')
        relations = tree.xpath(f'//table[@id = "characterlist_{id}"]/tbody/tr')
        rel_array = {}
        for relation in relations:
            if "id" in relation.attrib.keys():
                rel_type = relation.xpath('./td[@class = "reltype"]/text()')[0]
                rel_array.update({rel_type: []})
            key = relation.xpath('./td[@class = "name char"]/a/@href')[0]
            entity = relation.xpath('./td[@class = "entity"]/text()')[0].strip().split(',')[0]
            rel_array.get(rel_type).append({'id':key.split('/')[2], 'entity' : entity})
        json_shiki = {}
        for anime in animes:
            json_shiki.update({anime:get_shiki_anime(anime)})
        info_json = {"anime" : json_shiki,
                     "relations" : rel_array}
        character_json ={}
        for row in main_info:
            field = row.xpath('./th/text()')[0]
            value = []
            value += row.xpath('./td[@class = "value"]//span[@class = "tagname"]/node()') 
            value += row.xpath('./td[@class = "value"]//span[@itemprop]/node() | ./td[@class = "value"]//label[@itemprop]/node()')
            value += row.xpath('./td[@class = "value"]/text()[not(../span)]')
            value += row.xpath('./td[@class = "value"]//span[@class = "date"]/text()')
            value += row.xpath('./td[@class = "value"]//span[@class = "time"]/text()') 
            value += row.xpath('./td[@class = "value"]//span[@class = "value"]/text()')
            value += row.xpath('./td[@class = "value"]//span[@class = "count"]/text()') 

            if(len(value)>1):
                character_json.update({field : value})
            else:
                if(len(value)==0):
                    character_json.update({field : ""})
                else:
                    character_json.update({field : value[0]})

        if(character_json == {}):
            print('AniDb ban...')
            change_proxy()
            parse_ani_db_page(id)
        info_json.update({"characteristics" : keys_to_lower(character_json)})
        return info_json
    except:
        print('Error parsing...')
        change_proxy()
        return parse_ani_db_page(id)

def get_shiki_url(anime_name): #return first searched anime by name
    r = session_wp.get(f'https://shikimori.one/api/animes/search?q={anime_name}')
    if(r.status_code == 200):
        search = json.loads(r.text)
        return f'https://shikimori.one{search[0]["url"]}'
    else:
        print("Error while get shiki url...")
        time.sleep(10)
        return get_shiki_url(anime_name)

def get_shiki_anime(animeName): #return first searched anime by name
    search = get_shiki_response(f'/animes/search?q={animeName}')
    if(len(search)):
        anime = get_shiki_response(f'/animes/{search[0]["id"]}')
        return anime
    else:
        return {}

def get_shiki_response(path):
    r = session_wp.get(f'{BASE_URL_SHIKI}{path}')

    if r.status_code == 200:
        time.sleep(1)
        return json.loads(r.text)
    else:
        print('Error')
        time.sleep(4)
        return get_shiki_response(path)    

def keys_to_lower(dict):
    temp = {}
    for k in dict.keys():
        temp.update({k.lower():dict[k]})
    return temp

def main():
    db = get_database()
    with open('jsons/raw/characters.json', 'r+', encoding='utf-8') as file:
        data = json.load(file)
        print(len(data))
        file.close()
        
        bar = IncrementalBar('Characters', max = len(data))
        for i in data:
            bar.next()
            test = db["Characters"].find_one({"id": i["id"]})
            if test == None:
                if 'info' not in i.keys():
                    v = parse_ani_db_page(i["id"])
                    if(v != {}):
                        i.update({'info': v })
                        try:
                            db["Characters"].insert_one(i)
                            time.sleep(2)
                        except:
                            print("")
                else:
                    try:
                        db["Characters"].insert_one(i)
                    except:
                        print("")

        bar.finish()
                
def get_database():
    
    CONNECTION_STRING = "mongodb://root:pass12345@localhost:27017/"

    client = MongoClient(CONNECTION_STRING)

    return client['AniDb']

if __name__ == '__main__':
    # v = parseAniDbPage(98645)
    # print(v)
    get_proxies()
    change_proxy()
    main()


