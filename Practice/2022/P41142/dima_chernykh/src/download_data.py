import os
import pokebase as pb
import requests
import json

pokedex_url = 'https://pokeapi.glitch.me/v1'

headers = {
    'User-Agent': 'BastionDiscordBot (https://bastionbot.org, v6.16.1)'
}

def make_request(path):
        res = requests.get(path, headers=headers)
        if res.ok or res.status_code == 404:
            return res.json()
        else:
            return res.raise_for_status()



def get_pokemon_by_name(name):
        endpoint = '/pokemon/' + str(name)
        print(pokedex_url + endpoint)
        return make_request(pokedex_url + endpoint)



def download_from_pokeapi():
    pokemons = pb.APIResourceList('pokemon')
    with open('pokemons_data.json', 'r') as file:
        pokemons_data = json.loads(file.read())
    entries_len = len(pokemons_data)
    for pokemon in pokemons:
        if entries_len != 0:
            entries_len = entries_len - 1
            continue
        name = pokemon['name']
        pokemons_data.append(get_pokemon_by_name(name))
        print(len(pokemons) - len(pokemons_data))
        with open('pokemons_data.json', 'w') as file:
            file.write(json.dumps(pokemons_data, indent=4))


def process_new_format():
    with open('pokemons_data.json', 'r') as file:
        pokemons_data = json.loads(file.read())
        new_format = {}
        for index, pokemon in enumerate(pokemons_data):
            data = pokemon[0] if type(pokemon) == list else pokemon
            if 'name' in data.keys():
                del(data['abilities'])
                del(data['eggGroups'])
                del(data['gender'])
                del(data['height'])
                del(data['weight'])
                data['evolutionLine'] = data['family']['evolutionLine']
                del(data['family'])
                del(data['starter'])
                del(data['legendary'])
                del(data['mythical'])
                del(data['ultraBeast'])
                del(data['mega'])
                del(data['gen'])
                del(data['sprite'])
            name = data['name'] if 'name' in data.keys() else f'error-{index}'
            new_format[name] = data
    with open('pokemons.json', 'w') as file:
        file.write(json.dumps(new_format, indent=4))


def add_pokebase_data():
    with open('pokemons.json', 'r') as file:
        data = json.loads(file.read())
        all = len(data)
        count = len(data)
        data_list = list(data)
        for pokemon_name in data_list:
            print(f'{all-count}/{all}')
            count = count - 1
            if 'error' not in pokemon_name:
                print(f'{pokemon_name}')
                pokemon_data = pb.APIResource('pokemon', pokemon_name.lower())
                stats = {str(stat.stat): int(stat.base_stat) for stat in pokemon_data.stats if str(stat.stat) not in ('special-attack', 'special-defense')}
                data[pokemon_name].update(stats)
                data[pokemon_name]['weight'] = pokemon_data.weight
                data[pokemon_name]['height'] = pokemon_data.height
                data[pokemon_name]['types'] = [str(p_type.type.name) for p_type in pokemon_data.types]
                data[pokemon_name]['moves'] = [str(move.move.name) for move in pokemon_data.moves]
                data[pokemon_name]['species'] = pokemon_data.species.name
                with open('pokemons.json', 'w') as file:
                    file.write(json.dumps(data, indent=4))
            else:
                del(data[pokemon_name])
                continue


def download_types_from_pokebase():
    types = {}
    for p_type in pb.APIResourceList('type'):
        pp_type = pb.APIResource('type', p_type['name'])
        damage_relations = {}
        damage_relations['double_damage_from'] = [str(damage) for damage in pp_type.damage_relations.double_damage_from]
        damage_relations['double_damage_to'] = [str(damage) for damage in pp_type.damage_relations.double_damage_to]
        damage_relations['half_damage_from'] = [str(damage) for damage in pp_type.damage_relations.half_damage_from]
        damage_relations['half_damage_to'] = [str(damage) for damage in pp_type.damage_relations.half_damage_to]
        damage_relations['no_damage_from'] = [str(damage) for damage in pp_type.damage_relations.no_damage_from]
        damage_relations['no_damage_to'] = [str(damage) for damage in pp_type.damage_relations.no_damage_to]
        types[pp_type.name] = {
            'damage_relations': damage_relations,
        }
    with open('types.json', 'w') as file:
        file.write(json.dumps(types, indent=4))


def download_moves_from_pokebase():
    move_items = pb.APIResourceList('move')
    moves_data = {}
    if os.path.exists('moves.json'):
        with open('moves.json', 'r') as file:
            moves_data = json.loads(file.read()) 
    
    count_cloud = len(move_items)
    count_local = len(moves_data)
    for move_item in move_items:
        if count_local != 0:
            count_local = count_local - 1
            continue
        count_cloud = count_cloud - 1

        move = pb.APIResource('move', move_item['name'])
        moves_data[move.name] = {
            'description': move.effect_entries[0].short_effect if len(move.effect_entries) != 0 else 'no description',
            'type': move.type.name
        }
        with open('moves.json', 'w') as file:
            file.write(json.dumps(moves_data, indent=4))


def execute():
    # download_from_pokeapi()
    # process_new_format()
    # download_types_from_pokebase()
    # download_moves_from_pokebase()
    add_pokebase_data()

execute()