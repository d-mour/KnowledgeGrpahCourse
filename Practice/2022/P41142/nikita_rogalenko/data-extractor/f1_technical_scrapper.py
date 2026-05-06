import urllib.request as urllib_request
import bs4 as bs
from datetime import datetime
import json


BASE_URL = "https://www.f1technical.net"
F1_START_YEAR = 1950
F1_CURRENT_YEAR = datetime.now().year


def save_json_to_file(json_data, file_path):
    data_to_write = json.dumps(json_data, indent=4)
    file = open(file_path, 'w+')
    file.write(data_to_write)
    file.close()


def get_page_html(url):
    page = urllib_request.urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    return html


def process_team_page(team):
    html = get_page_html(team['f1_technical_url'])
    soup = bs.BeautifulSoup(html, features="html.parser")
    try:
        main_info_block = soup.select_one(".intro").findAll("b")
        for part in main_info_block:
            team[part.string.lower().replace(" ", "_")[:-1]] = part.nextSibling
    except AttributeError:
        print("No link for team " + team["name"])
    return team


def process_car_page(car):
    html = get_page_html(car['f1_technical_url'])
    soup = bs.BeautifulSoup(html, features="html.parser")
    try:
        main_info_block = soup.select_one(".intro").findAll("b")
        for part in main_info_block:
            if part.string.lower()[:-1] != "team":
                car[part.string.lower().replace(" ", "_")[:-1]] = part.nextSibling
        specs_block = soup.select_one(".article").findAll("h2")
        for part in specs_block:
            car[part.string.lower().replace(" ", "_")] = part.nextSibling.nextSibling.getText()
    except AttributeError:
        print("No link for car " + car["model"])
    return car


def get_f1_technical_data(results_dir_path):
    cars_dict = {}
    teams_dict = {}
    for year in range(F1_START_YEAR, F1_CURRENT_YEAR + 1):
        html = get_page_html(BASE_URL + f'/f1db/cars/years/{year}')
        soup = bs.BeautifulSoup(html, features="html.parser")
        hrefs_list = list(tag.get("href").split("?")[0] for tag in soup.findAll("table")[0].findAll("a"))
        names_list = list(tag.string for tag in soup.findAll("table")[0].findAll("a"))
        for i, name in enumerate(names_list):
            name_id = name.lower().replace(" ", "_")
            if '/cars/' in hrefs_list[i]:
                if name_id in cars_dict:
                    if year not in cars_dict[name_id]["years"]:
                        cars_dict[name_id]["years"].append(year)
                else:
                    cars_dict[name_id] = {
                        "model": name,
                        "team": names_list[i+1].lower().replace(" ", "_"),
                        "f1_technical_url": BASE_URL + hrefs_list[i],
                        "years": [year]
                    }
                    process_car_page(cars_dict[name_id])
            if '/teams/' in hrefs_list[i]:
                if name_id in teams_dict:
                    if year not in teams_dict[name_id]["years"]:
                        teams_dict[name_id]["years"].append(year)
                else:
                    teams_dict[name_id] = {
                        "name": name,
                        "f1_technical_url": BASE_URL + hrefs_list[i],
                        "years": [year]
                    }
                    process_team_page(teams_dict[name_id])
    save_json_to_file(teams_dict, results_dir_path + 'f1-technical-teams.json')
    save_json_to_file(cars_dict, results_dir_path + 'f1-technical-cars.json')
