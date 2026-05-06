import urllib.request as urllib_request
import urllib.parse as urllib_parse
from datetime import datetime
import os
import json


BASE_URL = "https://ergast.com/api/f1/"
F1_START_YEAR = 1950
F1_CURRENT_YEAR = datetime.now().year


def build_ergast_data_request_url(data_type, data_format, year, limit, offset):
    data_url = BASE_URL
    if year is not None:
        data_url += f'{year}/'
    if data_type is not None:
        data_url += f'{data_type}'
        if data_format is not None:
            data_url += f'.{data_format.lower()}'
    if limit is not None or offset is not None:
        data_url += '?'
        url_params = urllib_parse.urlencode(
            {param_name: param_value for param_name, param_value in (('limit', limit), ('offset', offset))
             if param_value is not None})
        data_url += url_params
    return data_url


def get_ergast_json_data_by_request(data_url):
    data_response = urllib_request.urlopen(data_url)
    data = json.load(data_response)
    return data


def save_json_to_file(json_data, file_path):
    data_to_write = json.dumps(json_data, indent=4)
    file = open(file_path, 'w+')
    file.write(data_to_write)
    file.close()


def load_ergast_json_from_file(file_path):
    json_file = open(file_path, 'r')
    result = json.load(json_file)
    json_file.close()
    return result


def parse_ergast_driver_data(json_driver_data):
    ergast_drivers_array = json_driver_data['MRData']['DriverTable']['Drivers']
    final_drivers_dict = {}
    print(ergast_drivers_array)
    for ergast_driver in ergast_drivers_array:
        driver = {
            'name': ergast_driver['givenName'],
            'surname': ergast_driver['familyName'],
            'birth_date': datetime.strptime(ergast_driver['dateOfBirth'], '%Y-%m-%d').date().strftime('%d.%m.%Y'),
            'nationality': ergast_driver['nationality'],
            'permanent_number': ergast_driver['permanentNumber'] if 'permanentNumber' in ergast_driver else ' ',
            'driver_code': ergast_driver['code'] if 'code' in ergast_driver else ' ',
            'wikipedia_page_url': ergast_driver['url'],
            'ergast_driver_id': ergast_driver['driverId']
        }
        final_drivers_dict[ergast_driver['driverId']] = driver
    return final_drivers_dict


def parse_ergast_constructor_data(json_constructor_data):
    ergast_constructors_array = json_constructor_data['MRData']['ConstructorTable']['Constructors']
    final_constructors_dict = {}
    print(ergast_constructors_array)
    for ergast_constructor in ergast_constructors_array:
        constructor = {
            'name': ergast_constructor['name'],
            'nationality': ergast_constructor['nationality'],
            'wikipedia_page_url': ergast_constructor['url'],
            'ergast_constructor_id': ergast_constructor['constructorId']
        }
        final_constructors_dict[ergast_constructor['constructorId']] = constructor
    return final_constructors_dict


def parse_ergast_circuit_data(json_circuit_data):
    ergast_circuits_array = json_circuit_data['MRData']['CircuitTable']['Circuits']
    final_circuits_dict = {}
    print(ergast_circuits_array)
    for ergast_circuit in ergast_circuits_array:
        circuit = {
            'name': ergast_circuit['circuitName'],
            'locality': ergast_circuit['Location']['locality'],
            'country': ergast_circuit['Location']['country'],
            'latitude': ergast_circuit['Location']['lat'],
            'longitude': ergast_circuit['Location']['long'],
            'wikipedia_page_url': ergast_circuit['url'],
            'ergast_circuit_id': ergast_circuit['circuitId']
        }
        final_circuits_dict[ergast_circuit['circuitId']] = circuit
    return final_circuits_dict


def parse_ergast_season_data(json_season_data):
    ergast_seasons_array = json_season_data['MRData']['SeasonTable']['Seasons']
    final_seasons_dict = {}
    print(ergast_seasons_array)
    for ergast_season in ergast_seasons_array:
        season = {
            'year': ergast_season['season'],
            'wikipedia_page_url': ergast_season['url']
        }
        final_seasons_dict[ergast_season['season']] = season
    return final_seasons_dict


def parse_ergast_races_data(json_races_data):
    ergast_races_array = json_races_data['MRData']['RaceTable']['Races']
    final_races_dict = {}
    print(ergast_races_array)
    for ergast_race in ergast_races_array:
        race = {
            'season': ergast_race['season'],
            'round': ergast_race['round'],
            'name': ergast_race['raceName'],
            'date': datetime.strptime(ergast_race['date'], '%Y-%m-%d').date().strftime('%d.%m.%Y'),
            'time': ergast_race['time'] if 'time' in ergast_race else '',
            'ergast_circuit_id': ergast_race['Circuit']['circuitId'],
            'wikipedia_page_url': ergast_race['url']
        }
        final_races_dict[f"{ergast_race['season']} {ergast_race['raceName']}".lower().replace(" ", "_")] = race
    return final_races_dict


def parse_ergast_qualifying_data(json_qualifying_data):
    ergast_races_array = json_qualifying_data['MRData']['RaceTable']['Races']
    final_qualifying_dict = {}
    for ergast_race in ergast_races_array:
        ergast_qualifying_array = ergast_race['QualifyingResults']
        print(ergast_qualifying_array)
        championship = f"{ergast_race['season']} {ergast_race['raceName']}".lower().replace(" ", "_")
        final_qualifying_array = []
        for ergast_qualifying in ergast_qualifying_array:
            qualifying = {
                'number': ergast_qualifying['number'],
                'position': ergast_qualifying['position'],
                'ergast_driver_id': ergast_qualifying['Driver']['driverId'],
                'ergast_constructor_id': ergast_qualifying['Constructor']['constructorId'],
                'Q1': ergast_qualifying['Q1'] if 'Q1' in ergast_qualifying else ' ',
                'Q2': ergast_qualifying['Q2'] if 'Q2' in ergast_qualifying else ' ',
                'Q3': ergast_qualifying['Q3'] if 'Q3' in ergast_qualifying else ' '
            }
            final_qualifying_array.append(qualifying)
        final_qualifying_dict[championship] = final_qualifying_array
    return final_qualifying_dict


def parse_ergast_race_results_data(json_race_results_data):
    ergast_races_array = json_race_results_data['MRData']['RaceTable']['Races']
    final_race_results_dict = {}
    for ergast_race in ergast_races_array:
        ergast_race_results_array = ergast_race['Results']
        print(ergast_race_results_array)
        championship = f"{ergast_race['season']} {ergast_race['raceName']}".lower().replace(" ", "_")
        final_race_results_array = []
        for ergast_race_result in ergast_race_results_array:
            race_result = {
                'number': ergast_race_result['number'],
                'position': ergast_race_result['position'],
                'position_text': ergast_race_result['positionText'],
                'points': ergast_race_result['points'],
                'ergast_driver_id': ergast_race_result['Driver']['driverId'],
                'ergast_constructor_id': ergast_race_result['Constructor']['constructorId'],
                'grid': ergast_race_result['grid'],
                'laps': ergast_race_result['laps'],
                'status': ergast_race_result['status'],
                'time': ergast_race_result['Time']['time'] if 'Time' in ergast_race_result else ''
            }
            final_race_results_array.append(race_result)
        final_race_results_dict[championship] = final_race_results_array
    return final_race_results_dict


def parse_ergast_driver_standings_data(json_driver_standings_data):
    ergast_standings_array = json_driver_standings_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    season_with_final_round = f"{json_driver_standings_data['MRData']['StandingsTable']['StandingsLists'][0]['season']}_" \
                              f"{json_driver_standings_data['MRData']['StandingsTable']['StandingsLists'][0]['round']}"
    final_standings_dict = {}
    print(ergast_standings_array)
    final_season_standings_array = []
    for ergast_standing in ergast_standings_array:
        standing = {
            'position': ergast_standing['position'],
            'position_text': ergast_standing['positionText'],
            'points': ergast_standing['points'],
            'wins': ergast_standing['wins'],
            'ergast_driver_id': ergast_standing['Driver']['driverId'],
            'constructors': []
        }
        constructors_list = ergast_standing['Constructors']
        for constructor in constructors_list:
            standing['constructors'].append(constructor['constructorId'])
        final_season_standings_array.append(standing)
    final_standings_dict[season_with_final_round] = final_season_standings_array
    return final_standings_dict


def parse_ergast_constructor_standings_data(json_constructor_standings_data):
    try:
        ergast_standings_array = json_constructor_standings_data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    except IndexError:
        return
    season_with_final_round = f"{json_constructor_standings_data['MRData']['StandingsTable']['StandingsLists'][0]['season']}_" \
                              f"{json_constructor_standings_data['MRData']['StandingsTable']['StandingsLists'][0]['round']}"
    final_standings_dict = {}
    print(ergast_standings_array)
    final_season_standings_array = []
    for ergast_standing in ergast_standings_array:
        standing = {
            'position': ergast_standing['position'],
            'position_text': ergast_standing['positionText'],
            'points': ergast_standing['points'],
            'wins': ergast_standing['wins'],
            'ergast_constructor_id': ergast_standing['Constructor']['constructorId'],
        }
        final_season_standings_array.append(standing)
    final_standings_dict[season_with_final_round] = final_season_standings_array
    return final_standings_dict


# process f1 data from ergast api
# arg - dir with output files
def process_f1_ergast_data(results_dir_path):
    if not os.path.exists(results_dir_path):
        os.makedirs(results_dir_path)

    drivers_url = build_ergast_data_request_url("drivers", "json", None, 1000, None)
    drivers_ergast_data = get_ergast_json_data_by_request(drivers_url)
    drivers_data = parse_ergast_driver_data(drivers_ergast_data)
    save_json_to_file(drivers_data, results_dir_path + 'ergast-drivers.json')
    
    constructors_url = build_ergast_data_request_url("constructors", "json", None, 300, None)
    constructors_ergast_data = get_ergast_json_data_by_request(constructors_url)
    constructors_data = parse_ergast_constructor_data(constructors_ergast_data)
    save_json_to_file(constructors_data, results_dir_path + 'ergast-constructors.json')

    circuits_url = build_ergast_data_request_url("circuits", "json", None, 100, None)
    circuits_ergast_data = get_ergast_json_data_by_request(circuits_url)
    circuits_data = parse_ergast_circuit_data(circuits_ergast_data)
    save_json_to_file(circuits_data, results_dir_path + 'ergast-circuits.json')
    
    seasons_url = build_ergast_data_request_url("seasons", "json", None, 100, None)
    seasons_ergast_data = get_ergast_json_data_by_request(seasons_url)
    seasons_data = parse_ergast_season_data(seasons_ergast_data)
    save_json_to_file(seasons_data, results_dir_path + 'ergast-seasons.json')

    races_data = {}
    for year in range(F1_START_YEAR, int(F1_CURRENT_YEAR) + 1):
        races_url = f"https://ergast.com/api/f1/{year}.json?limit=100"
        races_ergast_data_by_year = get_ergast_json_data_by_request(races_url)
        races_data_by_year = parse_ergast_races_data(races_ergast_data_by_year)
        races_data = {**races_data, **races_data_by_year}
    save_json_to_file(races_data, results_dir_path + 'ergast-races.json')

    qualifying_data = {}
    for year in range(F1_START_YEAR, int(F1_CURRENT_YEAR) + 1):
        qualifying_url = build_ergast_data_request_url("qualifying", "json", year, 1000, None)
        qualifying_ergast_data_by_year = get_ergast_json_data_by_request(qualifying_url)
        qualifying_data_by_year = parse_ergast_qualifying_data(qualifying_ergast_data_by_year)
        qualifying_data = {**qualifying_data, **qualifying_data_by_year}
    save_json_to_file(qualifying_data, results_dir_path + 'ergast-qualifying.json')

    race_results_data = {}
    for year in range(F1_START_YEAR, int(F1_CURRENT_YEAR) + 1):
        race_results_url = build_ergast_data_request_url("results", "json", year, 1000, None)
        race_results_ergast_data_by_year = get_ergast_json_data_by_request(race_results_url)
        race_results_data_by_year = parse_ergast_race_results_data(race_results_ergast_data_by_year)
        race_results_data = {**race_results_data, **race_results_data_by_year}
    save_json_to_file(race_results_data, results_dir_path + 'ergast-results.json')

    driver_standings_data = {}
    for year in range(F1_START_YEAR, int(F1_CURRENT_YEAR) + 1):
        driver_standings_url = build_ergast_data_request_url("driverstandings", "json", year, 1000, None)
        driver_standings_ergast_data_by_year = get_ergast_json_data_by_request(driver_standings_url)
        driver_standings_data_by_year = parse_ergast_driver_standings_data(driver_standings_ergast_data_by_year)
        driver_standings_data = {**driver_standings_data, **driver_standings_data_by_year}
    save_json_to_file(driver_standings_data, results_dir_path + 'ergast-driver-standings.json')

    constructor_standings_data = {}
    for year in range(F1_START_YEAR, int(F1_CURRENT_YEAR) + 1):
        constructor_standings_url = build_ergast_data_request_url("constructorstandings", "json", year, 1000, None)
        constructor_standings_ergast_data_by_year = get_ergast_json_data_by_request(constructor_standings_url)
        constructor_standings_data_by_year = parse_ergast_constructor_standings_data(constructor_standings_ergast_data_by_year)
        if constructor_standings_data_by_year:
            constructor_standings_data = {**constructor_standings_data, **constructor_standings_data_by_year}
    save_json_to_file(constructor_standings_data, results_dir_path + 'ergast-constructor-standings.json')
