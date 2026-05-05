import json
import string

# substrings to search for in plot description
drivers_list = []   # list of drivers names
seasons_list = []   # list of seasons years
teams_list = []     # list of teams names
cars_list = []      # list of cars models
grand_prixes_list = []  # list of GP names


def load_json_from_file(file_path):
    json_file = open(file_path, 'r')
    result = json.load(json_file)
    json_file.close()
    return result


def get_amount_of_driver_surname(surname):
    surnames_num = 0
    for driver in drivers_list:
        if driver["surname"] == surname:
            surnames_num += 1
    return surnames_num


def fill_data_lists():
    drivers_json = load_json_from_file("../f1_extracted_data/ergast-drivers.json")
    for driver in drivers_json:
        drivers_list.append(
            {
                "name": drivers_json[driver]["name"],
                "surname": drivers_json[driver]["surname"]
            }
        )
    teams_json = load_json_from_file("../f1_extracted_data/ergast-constructors.json")
    for team in teams_json:
        teams_list.append(teams_json[team]["name"])
    cars_json = load_json_from_file("../f1_extracted_data/f1-technical-cars.json")
    for car in cars_json:
        cars_list.append(cars_json[car]["model"])
    seasons_json = load_json_from_file("../f1_extracted_data/ergast-seasons.json")
    seasons_list.extend(seasons_json.keys())
    grand_prix_json = load_json_from_file("../f1_extracted_data/ergast-races.json")
    for grand_prix in grand_prix_json:
        grand_prixes_list.append(grand_prix_json[grand_prix]["name"])


# extracting data what movie/book is about by title and plot description
def get_what_creation_is_about(title, plot, addit_info):
    description = f'{title} {plot} {addit_info if addit_info else ""}'.translate(str.maketrans('', '', string.punctuation)).lower()
    is_about_dict = {}
    for driver in drivers_list:
        if f' {driver["surname"].lower()} ' in description:
            is_about_dict.setdefault("drivers", [])
            same_surnames_count = get_amount_of_driver_surname(driver["surname"])
            if same_surnames_count < 2:
                is_about_dict["drivers"].append(f'{driver["name"]} {driver["surname"]}')
            if same_surnames_count >= 2 and f' {driver["name"].lower()} ' in description:
                is_about_dict["drivers"].append(f'{driver["name"]} {driver["surname"]}')
    for car in cars_list:
        if car.lower() in description:
            is_about_dict.setdefault("cars", [])
            is_about_dict["cars"].append(car)
    for team in teams_list:
        if f' {team.lower().replace("team", "").strip()} ' in description:
            is_about_dict.setdefault("teams", [])
            is_about_dict["teams"].append(team)
    for season in seasons_list:
        if season in description:
            is_about_dict.setdefault("seasons", [])
            if (season + "s") in description:
                for year in range(int(season), int(season) + 10):
                    is_about_dict["seasons"].append(str(year))
            else:
                is_about_dict["seasons"].append(season)
    for grand_prix in grand_prixes_list:
        if grand_prix.lower() in description:
            is_about_dict.setdefault("grand_prixes", [])
            if grand_prix not in is_about_dict["grand_prixes"]:
                is_about_dict["grand_prixes"].append(grand_prix)
    # print(is_about_dict)
    return is_about_dict
