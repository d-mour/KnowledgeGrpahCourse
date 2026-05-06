import requests

# Ваш API-ключ, полученный на портале разработчиков Riot Games
API_KEY = 'RGAPI-d21a52b7-791d-4865-9d84-db42937aebf1'

# Базовый URL для доступа к API
BASE_URL = 'https://na.api.riotgames.com/val/content/v1/contents'

# Параметры для запроса (например, язык данных)
HEADERS = {
    'X-Riot-Token': API_KEY
}

def get_valorant_agents():
    response = requests.get(BASE_URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        agents = [item['name'] for item in data['characters']]
        agents.remove("Sova")
        agents.remove("Null UI Data!")
        return agents
    else:
        print(f"Error: {response.status_code}")
        return []

def get_valorant_maps():
    response = requests.get(BASE_URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        maps = [item['name'] for item in data['maps']]
        maps.remove("Null UI Data!")
        return maps
    else:
        print(f"Error: {response.status_code}")
        return []
