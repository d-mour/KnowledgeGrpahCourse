import json

def save_agents_to_json(agents):
    with open('data/agents.json', 'w', encoding='utf-8') as f:
        json.dump(agents, f, ensure_ascii=False, indent=4)
    print("Список агентов сохранен в agents.json")


def load_agents_from_json(filename='data/agents.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        return agents
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле {filename}.")
        return []
    



def save_maps_to_json(maps):
    with open('data/maps.json', 'w', encoding='utf-8') as f:
        json.dump(maps, f, ensure_ascii=False, indent=4)
    print("Список агентов сохранен в agents.json")


def load_maps_from_json(filename='data/maps.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            maps = json.load(f)
        return maps
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле {filename}.")
        return []
    


def save_ranks_to_json(ranks):
    with open('data/ranks.json', 'w', encoding='utf-8') as f:
        json.dump(ranks, f, ensure_ascii=False, indent=4)
    print("Список рангов сохранен в agents.json")

def load_ranks_from_json(filename='data/ranks.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            ranks = json.load(f)
        return ranks
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле {filename}.")
        return []