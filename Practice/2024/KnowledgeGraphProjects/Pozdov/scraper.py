import requests
from enum import Enum
from bs4 import BeautifulSoup
import csv
import os

class PlayerStatsGame(dict):
    def __init__(self):
        self = {}

    def add(self, key, el):
        self[key] = el

    def retrieve(self, key):
        return self[key]

    def display(self):
        print(self)

class Team():
    def __init__(self, name=""):
        self.name = name
        self.players = []

    def display(self):
        print(f"\tname: {self.name}")
        print(f"\tplayers: {self.players}")


class Game():
    def __init__(self, name=None, stats=[], part_of_series="", team_winner=None, team_loser=None, goals_winner=0, goals_loser=0):
        self.name = name
        self.stats = stats
        self.part_of_series = part_of_series
        self.team_winner = team_winner
        self.team_loser = team_loser
        self.goals_winner = goals_winner
        self.goals_loser = goals_loser

    def display(self):
        print(f"\tname: {self.name}")
        print(f"\tpart_of_series: {self.part_of_series}")
        print(f"\tteam_winner: {self.team_winner.name}")
        print(f"\tteam_loser: {self.team_loser.name}")
        print(f"\tgoals_winner: {self.goals_winner}")
        print(f"\tgoals_loser: {self.goals_loser}")
        print(f"\tstats player1: {self.stats[0].retrieve("name")}")

class Series():
    def __init__(self, games=[], name=None,  team_winner=None, team_loser=None, score_winner=0, score_loser=0, best_of=0):
        self.games = games
        self.name = name
        self.team_winner = team_winner
        self.team_loser = team_loser
        self.score_winner = score_winner
        self.score_loser = score_loser
        self.best_of = best_of

    def add_game(self, link_name):
        self.games.append(link_name)

    def display(self):
        print(f"name: {self.name}")
        print(f"team_winner: {self.team_winner.name}")
        print(f"players:  {self.team_winner.players}")
        print(f"team_loser: {self.team_loser.name}")
        print(f"players:  {self.team_loser.players}")
        print(f"score_winner: {self.score_winner}")
        print(f"score_loser: {self.score_loser}")
        print(f"games played: {len(self.games)}")

        for i, game in enumerate(self.games, start=1):
            print(f"game {i}:")
            game.display()

class urltag(Enum):
    OVERVIEW = "overview"
    CORE = "core"
    BALL = "ball"
    DEMO = "demo"
    BOOST_TEAMS = "boost-teams"
    BOOST_PLAYERS = "boost-players"
    POSITIONING = "positioning"
    MOVEMENT_TEAMS= "movement-teams"
    MOVEMENT_PLAYERS = "movement-players"


def is_best_of_how_many(soup) -> int:
    num = soup.find('td', class_='res win')
    return (int(num.get_text()) - 1) * 2 + 1
    


def is_games_page(soup) -> bool:
    ul = soup.find('ul', class_="rgroups")
    if (ul == None):
        return True
    else:
        return False



def parse_links(link, links_list: list):
    r = requests.get("https://ballchasing.com" + link)
    soup = BeautifulSoup(r.content, 'html.parser')
    ul = soup.find('ul', class_="rgroups")
    if (ul.contents == ['\n']):
        links = soup.find_all("a", class_="replay-link")
        for l in links:
            links_list.append("https://ballchasing.com" + l['href'])
    else:
        li_elements = ul.find_all("li")
        for el in li_elements:
            h = el.find("h2", class_="group-title")
            href = h.find("a")["href"]
            parse_links(href, links_list)



def save_links_to_file(filename, links):
    with open(filename, "w") as file:
        for link in links:
            if link:
                file.write(link + "\n")



def parse_overview(link, stats):
    r = requests.get(link + f"#{urltag.CORE}")
    soup = BeautifulSoup(r.content, 'html.parser')
    soup = soup.find("div", id="cemetery").find("div", id="details-overview")

    timeline_rows = soup.find("tbody", class_="blue").find_all("tr", class_="timeline-row")
    for row in timeline_rows:
        row.decompose()
    timeline_rows = soup.find("tbody", class_="orange").find_all("tr", class_="timeline-row")
    for row in timeline_rows:
        row.decompose()

    blue_team_tr = soup.find("tbody", class_="blue").find_all("tr")
    for tr in blue_team_tr:
        stat = PlayerStatsGame()

        name = tr.find("td", class_="player-name").find("a").get_text()[:-4].strip()
        stat.add("name", name) 
        stat.add("played_for_side", "Blue")

        is_mvp = False if tr.find("i", class_="mvp fas fa-star") == None else True
        stat.add("is_mvp", is_mvp)

        car_span = tr.find("span", class_="car")
        car_icon_remove = car_span.find("i", class_="fas fa-car")

        if car_icon_remove:
            car_icon_remove.decompose()

        car = car_span.get_text().strip()
        stat.add("car", car)

        cells = tr.find_all("td")
        stat.add("score", int(cells[3].get_text()))
        stat.add("goals", int(cells[4].get_text()))
        stat.add("assists", int(cells[5].get_text()))
        stat.add("saves", int(cells[6].get_text()))
        stat.add("shots", int(cells[7].get_text()))

        stats.append(stat)
        
    orange_team_tr = soup.find("tbody", class_="orange").find_all("tr")
    for tr in orange_team_tr:
        stat = PlayerStatsGame()

        name = tr.find("td", class_="player-name").find("a").get_text()[:-4].strip()
        stat.add("name", name) 
        stat.add("played_for_side", "Orange")

        is_mvp = False if tr.find("i", class_="mvp fas fa-star") == None else True
        stat.add("is_mvp", is_mvp)

        car_span = tr.find("span", class_="car")
        car_icon_remove = car_span.find("i", class_="fas fa-car")

        if car_icon_remove:
            car_icon_remove.decompose()

        car = car_span.get_text().strip()
        stat.add("car", car)

        cells = tr.find_all("td")
        stat.add("score", int(cells[3].get_text()))
        stat.add("goals", int(cells[4].get_text()))
        stat.add("assists", int(cells[5].get_text()))
        stat.add("saves", int(cells[6].get_text()))
        stat.add("shots", int(cells[7].get_text()))

        stats.append(stat)

    return stats



def parse_boost(link, stats):
    r = requests.get(link + f"#{urltag.CORE}")
    soup = BeautifulSoup(r.content, 'html.parser')
    soup = soup.find("div", id="cemetery").find("div", id="details-boost-players")

    blue_team_tr = soup.find("tbody", class_="blue").find_all("tr")
    for i, tr in enumerate(blue_team_tr):
        cells = tr.find_all("td")
        stats[i].add("BPM", int(cells[1].get_text()))
        stats[i].add("average_boost", int(cells[2].get_text()))
        stats[i].add("time_0_boost", float(cells[3].get_text()[:-1]))
        stats[i].add("time_100_boost", float(cells[4].get_text()[:-1]))
        stats[i].add("boost_collected", int(cells[5].get_text()))
        stats[i].add("boost_stolen", int(cells[6].get_text()))
        stats[i].add("big_pads_collected", int(cells[7].get_text()))
        stats[i].add("small_pads_collected", int(cells[8].get_text()))
        stats[i].add("big_pads_stolen", int(cells[9].get_text()))
        stats[i].add("small_pads_stolen", int(cells[10].get_text()))
        stats[i].add("boost_used_supersonic", int(cells[11].get_text()))
        stats[i].add("boost_overfill", int(cells[12].get_text()))
        stats[i].add("boost_overfill_from_stolen", int(cells[13].get_text()))

    orange_team_tr = soup.find("tbody", class_="orange").find_all("tr")
    for i, tr in enumerate(orange_team_tr, start=3):
        cells = tr.find_all("td")
        stats[i].add("BPM", int(cells[1].get_text()))
        stats[i].add("average_boost", int(cells[2].get_text()))
        stats[i].add("time_0_boost", float(cells[3].get_text()[:-1]))
        stats[i].add("time_100_boost", float(cells[4].get_text()[:-1]))
        stats[i].add("boost_collected", int(cells[5].get_text()))
        stats[i].add("boost_stolen", int(cells[6].get_text()))
        stats[i].add("big_pads_collected", int(cells[7].get_text()))
        stats[i].add("small_pads_collected", int(cells[8].get_text()))
        stats[i].add("big_pads_stolen", int(cells[9].get_text()))
        stats[i].add("small_pads_stolen", int(cells[10].get_text()))
        stats[i].add("boost_used_supersonic", int(cells[11].get_text()))
        stats[i].add("boost_overfill", int(cells[12].get_text()))
        stats[i].add("boost_overfill_from_stolen", int(cells[13].get_text()))
    return stats



def parse_positioning(link, stats):
    r = requests.get(link + f"#{urltag.CORE}")
    soup = BeautifulSoup(r.content, 'html.parser')
    soup = soup.find("div", id="cemetery").find("div", id="details-positioning")

    blue_team_tr = soup.find("tbody", class_="blue").find_all("tr")
    for i, tr in enumerate(blue_team_tr):
        cells = tr.find_all("td")
        stats[i].add("defensive_third_percentage", float(cells[1].get_text().strip().split("(")[1][:-2]))
        stats[i].add("neutral_third_percentage", float(cells[2].get_text().strip().split("(")[1][:-2]))
        stats[i].add("offensive_third_percentage", float(cells[3].get_text().strip().split("(")[1][:-2]))
        stats[i].add("behind_ball_percentage", float(cells[6].get_text().strip().split("(")[1][:-2]))
        stats[i].add("ahead_of_ball_percentage", float(cells[7].get_text().strip().split("(")[1][:-2]))
        stats[i].add("avg_distance_ball", float(cells[8].get_text()))

    orange_team_tr = soup.find("tbody", class_="orange").find_all("tr")
    for i, tr in enumerate(orange_team_tr, start=3):
        cells = tr.find_all("td")
        stats[i].add("defensive_third_percentage", float(cells[1].get_text().strip().split("(")[1][:-2]))
        stats[i].add("neutral_third_percentage", float(cells[2].get_text().strip().split("(")[1][:-2]))
        stats[i].add("offensive_third_percentage", float(cells[3].get_text().strip().split("(")[1][:-2]))
        stats[i].add("behind_ball_percentage", float(cells[6].get_text().strip().split("(")[1][:-2]))
        stats[i].add("ahead_of_ball_percentage", float(cells[7].get_text().strip().split("(")[1][:-2]))
        stats[i].add("avg_distance_ball", float(cells[8].get_text()))
    return stats





def parse_movement(link, stats):
    r = requests.get(link + f"#{urltag.CORE}")
    soup = BeautifulSoup(r.content, 'html.parser')
    soup = soup.find("div", id="cemetery").find("div", id="details-movement-players")

    blue_team_tr = soup.find("tbody", class_="blue").find_all("tr")
    for i, tr in enumerate(blue_team_tr):
        cells = tr.find_all("td")
        stats[i].add("avg_speed_percentage", float(cells[2].get_text()[:-1]))
        stats[i].add("total_distance", int(cells[3].get_text()))
        stats[i].add("time_slow_speed", float(cells[4].get_text()[:-1]))
        stats[i].add("time_boost_speed", float(cells[5].get_text()[:-1]))
        stats[i].add("time_supersonic", float(cells[6].get_text()[:-1]))
        stats[i].add("time_on_ground", float(cells[7].get_text()[:-1]))
        stats[i].add("time_low_in_air", float(cells[8].get_text()[:-1]))
        stats[i].add("time_high_in_air", float(cells[9].get_text()[:-1]))
        stats[i].add("powerslide_duration", float(cells[10].get_text().split("/")[0][:-1]))
        stats[i].add("powerslide_count", int(cells[11].get_text()))
    
    orange_team_tr = soup.find("tbody", class_="orange").find_all("tr")
    for i, tr in enumerate(orange_team_tr, start=3):
        cells = tr.find_all("td")
        stats[i].add("avg_speed_percentage", float(cells[2].get_text()[:-1]))
        stats[i].add("total_distance", int(cells[3].get_text()))
        stats[i].add("time_slow_speed", float(cells[4].get_text()[:-1]))
        stats[i].add("time_boost_speed", float(cells[5].get_text()[:-1]))
        stats[i].add("time_supersonic", float(cells[6].get_text()[:-1]))
        stats[i].add("time_on_ground", float(cells[7].get_text()[:-1]))
        stats[i].add("time_low_in_air", float(cells[8].get_text()[:-1]))
        stats[i].add("time_high_in_air", float(cells[9].get_text()[:-1]))
        stats[i].add("powerslide_duration", float(cells[10].get_text().split("/")[0][:-1]))
        stats[i].add("powerslide_count", int(cells[11].get_text()))

    return stats

def parse_replay(link):
    stats = []
    stats = parse_overview(link, stats)
    stats = parse_boost(link, stats)
    stats = parse_positioning(link, stats)
    stats = parse_movement(link, stats)
    return stats

def parse_series(link):
    series = Series([], link)
    r = requests.get("https://ballchasing.com" + link + f"#{urltag.CORE}")
    soup = BeautifulSoup(r.content, 'html.parser')
    series.best_of = is_best_of_how_many(soup)
    game_links = soup.find_all("a", class_="replay-link")
    soup = soup.find("table", class_="table is-bordered").find("tbody")
    rows = soup.find_all("tr")

    games_count = int(rows[0].find("td").get_text().strip()) + int(rows[1].find("td").get_text().strip())

    games = [Game() for _ in range(games_count)]

    cells1 = rows[0].find_all("td")
    cells2 = rows[1].find_all("td")
    score1 = int(cells1[0].get_text().strip())
    score2 = int(cells2[0].get_text().strip())
    team1 = Team(cells1[1].find("h3").get_text().strip())
    team2 = Team(cells2[1].find("h3").get_text().strip())
    
    for el in cells1[1].find_all("span"):
        player_name = el.get_text().strip()
        if player_name:
            team1.players.append(player_name)

    for el in cells2[1].find_all("span"):
        player_name = el.get_text().strip()
        if player_name:
            team2.players.append(player_name)
   

    if (score1 > score2):
        series.score_winner = score1
        series.team_winner = team1
        series.score_loser = score2
        series.team_loser = team2
    else:
        series.score_winner = score2
        series.team_winner = team2
        series.score_loser = score1
        series.team_loser = team1

    for i, game in enumerate(games, start=2):
        game_name = game_links[i-2]['href'] 
        game.name = game_name
        game_score1 = cells1[i].get_text().strip()
        game_score2 = cells2[i].get_text().strip()

        if (game_score1 > game_score2):
            game.goals_winner = game_score1
            game.team_winner = team1
            game.goals_loser = game_score2
            game.team_loser = team2
        else:
            game.goals_winner = game_score2
            game.team_winner = team2
            game.goals_loser = game_score1
            game.team_loser = team1
        
        stats = parse_replay("https://ballchasing.com" + game_name)
        game.stats = stats
        game.part_of_series = series.name

    series.games = games
    return series


def parse_many_series(links = [
        "/group/bds-vs-elv-t11lrnk4f7",
        "/group/flcn-vs-og-009x9v4alh",
        "/group/g2-vs-qtp-0hfrv0vkvg",
        "/group/ggm1-vs-pwr-97s0jbpngn",
        "/group/gm8a-vs-r1-rfoecv00d0",
        "/group/gm8a-vs-r1-rfoecv00d0",
        "/group/lg-vs-fur-qsj2hrsgkh",
        "/group/vit-vs-col-rf46tp7kv5"
    ]):
    many_series = [parse_series(link) for link in links]
    return many_series

def create_csv():
    csv_filename = "game_stats.csv"
    header = [
        "game_name", "series_name", "team_winner", "team_loser", 
        "goals_winner", "goals_loser", "player_name", "played_for_side", 
        "is_mvp", "car", "score", "goals", "assists", "saves", "shots",
        "BPM", "average_boost", "time_0_boost", "time_100_boost", "boost_collected",
        "boost_stolen", "big_pads_collected", "small_pads_collected",
        "big_pads_stolen", "small_pads_stolen", "boost_used_supersonic", 
        "boost_overfill", "boost_overfill_from_stolen", "defensive_third_percentage",
        "neutral_third_percentage", "offensive_third_percentage", 
        "behind_ball_percentage", "ahead_of_ball_percentage", "avg_distance_ball",
        "avg_speed_percentage", "total_distance", "time_slow_speed", 
        "time_boost_speed", "time_supersonic", "time_on_ground", 
        "time_low_in_air", "time_high_in_air", "powerslide_duration", 
        "powerslide_count"
    ]

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()  

        for series in many_series:
            for game in series.games:
                for player_stats in game.stats:
                    player_data = {
                        "game_name": game.name,
                        "series_name": game.part_of_series,
                        "team_winner": game.team_winner.name,
                        "team_loser": game.team_loser.name,
                        "goals_winner": game.goals_winner,
                        "goals_loser": game.goals_loser,
                    }
                    player_data.update(player_stats)
                    writer.writerow(player_data)

    print(f"CSV file '{csv_filename}' has been created.")


if __name__ == "__main__":

    links = [
        # "/group/bds-vs-elv-t11lrnk4f7",
        # "/group/flcn-vs-og-009x9v4alh",
        # "/group/g2-vs-qtp-0hfrv0vkvg",
        # "/group/ggm1-vs-pwr-97s0jbpngn",
        # "/group/gm8a-vs-r1-rfoecv00d0",
        # "/group/gm8a-vs-r1-rfoecv00d0",
        # "/group/lg-vs-fur-qsj2hrsgkh",
        # "/group/vit-vs-col-rf46tp7kv5",
        # "/group/bds-vs-gm8a-xjwela6mxb",
        # "/group/col-vs-lg-j6xy31wj1l",
        # "/group/fur-vs-vit-jtxhqzsrxe",
        # "/group/g2-vs-ggm1-06d4jn2ypj",
        # "/group/kc-vs-flcn-ufvvv9jcka",
        # "/group/og-vs-lmt-bl0ry0pfv2",
        # "/group/pwr-vs-qtpg-or4l6oreb8",
        # "/group/r1-vs-elv-wzmkzx2h58",
        # "/group/bds-vs-pwr-5y0lzuujas",
        # "/group/elv-vs-qtpg-d2yt2q0idh",
        # "/group/fur-vs-ggm1-xqldkcwvnq",
        # "/group/g2-vs-r1-sk9tvgkbpx",
        # "/group/gm8a-vs-flcn-vh176zayx1",
        # "/group/kc-vs-col-myn7s39oz2",
        # "/group/lg-vs-lmt-kmfjg568uz",
        "/group/vit-vs-og-qp7enkbq8z",
    ]
    many_series = [parse_series(link) for link in links]

    csv_filename = "game_stats.csv"
    print(f"Updating CSV at: {os.path.abspath(csv_filename)}")

    header = [
        "game_name", "series_name", "team_winner", "team_loser", 
        "goals_winner", "goals_loser", "player_name", "played_for_side", 
        "is_mvp", "car", "score", "goals", "assists", "saves", "shots",
        "BPM", "average_boost", "time_0_boost", "time_100_boost", "boost_collected",
        "boost_stolen", "big_pads_collected", "small_pads_collected",
        "big_pads_stolen", "small_pads_stolen", "boost_used_supersonic", 
        "boost_overfill", "boost_overfill_from_stolen", "defensive_third_percentage",
        "neutral_third_percentage", "offensive_third_percentage", 
        "behind_ball_percentage", "ahead_of_ball_percentage", "avg_distance_ball",
        "avg_speed_percentage", "total_distance", "time_slow_speed", 
        "time_boost_speed", "time_supersonic", "time_on_ground", 
        "time_low_in_air", "time_high_in_air", "powerslide_duration", 
        "powerslide_count"
    ]

    file_exists = os.path.exists(csv_filename)
    try:
        with open(csv_filename, mode="a" if file_exists else "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            
            if not file_exists:
                writer.writeheader()

            for series in many_series:
                for game in series.games:
                    for player_stats in game.stats:
                        player_data = {
                            "game_name": game.name,
                            "series_name": game.part_of_series,
                            "team_winner": game.team_winner.name,
                            "team_loser": game.team_loser.name,
                            "goals_winner": game.goals_winner,
                            "goals_loser": game.goals_loser,
                            "player_name": player_stats['name'], 
                        }

                        filtered_stats = {k: player_stats[k] for k in header if k in player_stats}
                        if not filtered_stats:
                            print(f"No matching stats found for player {player_stats['name']}")
                        
                        player_data.update(filtered_stats)
                        
                        writer.writerow(player_data)

        print(f"CSV file '{csv_filename}' has been updated with new stats.")
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


