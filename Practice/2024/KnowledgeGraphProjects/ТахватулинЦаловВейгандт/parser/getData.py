from bs4 import BeautifulSoup
import json
import datetime
import asyncio
import aiohttp
import re

def parse_for_url(url, winrate):
    pattern = r"https://www.leagueofgraphs.com/champions/builds/([\w\s'. &]+)/vs-([\w\s'. &]+)/([\w\s]+)"
    match = re.match(pattern, url)
    
    if match:
        data = {
            "champion1" : match.group(1).strip(),
            "VsChampion" : match.group(2).strip(),
            "Rank" : match.group(3).strip(),
            "winrate" : winrate
        }
        dataInv = {
            "champion1" : match.group(2).strip(),
            "VsChampion" : match.group(1).strip(),
            "Rank" : match.group(3).strip(),
            "winrate" : 100 - winrate
        }
        return data, dataInv
    else:
        return "Invalid format"

async def get_element_with_retry(content, max_retries=1, delay=0.1):
    """ Ожидает появления элемента с id='graphDD2' в течение max_retries попыток """
    for _ in range(max_retries):
        soup = BeautifulSoup(str(content), "html.parser")
        place_for_find = soup.find(id="graphDD2")

        if place_for_find and place_for_find.contents:
            return place_for_find

        await asyncio.sleep(delay) 
    
    return None  

async def fetch(session, url):
        try:
            async with session.get(url, headers=headers) as response:
                return url, response.status, await response.text()
        except Exception as e:
            return url, "Ошибка", str(e)
    
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in url_list]
        results = await asyncio.gather(*tasks)

    # Вывод результатов
    for url, status, content in results:
        soup = BeautifulSoup(str(content), "html.parser")
        place_for_find = soup.find(id="graphDD2")
        try:
            winrate = float(str(place_for_find.contents[0]).replace(" ", "").replace("\n", '').replace("\\n", '').replace("%", ''))
            data, dataInv = parse_for_url(url, winrate=winrate)
            
            cp.writelines(json.dumps(data, indent=4) + ",\n")
            cp.writelines(json.dumps(dataInv, indent=4) + ",\n")
        except Exception as e:
            print("url " + url)
            logs.writelines("url: " + url)
            print(e)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}

# ranks = ["iron", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "master"]
ranks = ["platinum"]
cp = open(f"cp_chmp_vs_chmp_json_{ranks[0]}.json", 'a')

logs = open(f"logs.txt", "a")

champions = open("champs.txt", 'r')
rows = champions.readlines()
champion_list = []
for row in rows:
    champion_list.append(row.replace('\n', '').lower())


data_list = []
url_list = []
champ_was = []

cp.writelines("[")


startTime = datetime.datetime.now()

for champion in champion_list:
    champ_was.append(champion)
    for enemy in champion_list:
        for rank in ranks:
            if enemy == champion: continue
            if enemy in champ_was: continue
            url = f"https://www.leagueofgraphs.com/champions/builds/{champion}/vs-{enemy}/{rank}"
            url_list.append(url)

    asyncio.run(main())
    print(f"{champion} is Done. Time: {datetime.datetime.now() - startTime}")
    logs.writelines(f"{champion} is Done. Time: {datetime.datetime.now() - startTime}\n")
    
    url_list = []

cp.writelines("]")
print(datetime.datetime.now() - startTime)

cp.close()
champions.close()
