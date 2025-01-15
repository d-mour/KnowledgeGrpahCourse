from bs4 import BeautifulSoup
import os
from rdflib import Graph, Namespace, Literal, RDF


def parse_city_state(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    try:
        name = soup.find("div", class_="App_pageHeaderText__SsfWm").text.strip()

        inclination_element = soup.find(class_="StatBox_iconLabelCaption__i_uw4")
        inclination = inclination_element.text.strip() if inclination_element else None

        history_element = soup.find(string="Historical Context")
        history = (
            history_element.parent.parent.nextSibling.text.strip()
            if history_element
            else None
        )

        unique_ability_element = soup.find(string="Unique Ability")
        unique_ability_name = (
            unique_ability_element.parent.parent.parent.nextSibling.next_element.next_element.text.strip()
            if unique_ability_element
            else None
        )

        unique_ability_description = (
            unique_ability_element.parent.parent.parent.nextSibling.next_element.find_all(
                "p"
            )[
                1
            ].text.strip()
            if unique_ability_element
            else None
        )

        return {
            "name": name,
            "inclination": inclination,
            "history": history,
            "unique_ability_name": unique_ability_name,
            "unique_ability_description": unique_ability_description,
        }
    except Exception as e:
        print(f"Error parsing city state: {e}")
        return None


def process_city_states(folder_path, ns: Namespace, g: Graph, replace=False):
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".html") or not file_name.startswith("civilization_"):
            continue

        file_path = folder_path / file_name
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
            city_state_data = parse_city_state(html_content)

            if city_state_data:
                city_state_name = city_state_data["name"].strip().replace(" ", "_")
                city_state_individual = ns[city_state_name]

                if replace:
                    g.remove((city_state_individual, None, None))

                g.add((city_state_individual, RDF.type, ns.CityState))
                properties = {
                    ns.name: city_state_data["name"],
                    ns.history: city_state_data["history"],
                    ns.unique_ability_name: city_state_data["unique_ability_name"],
                    ns.unique_ability_description: city_state_data[
                        "unique_ability_description"
                    ],
                }
                for prop, value in properties.items():
                    if value:
                        g.add((city_state_individual, prop, Literal(value)))

                if city_state_data["inclination"]:
                    inclination_name = (
                        city_state_data["inclination"].strip().replace(" ", "_")
                    )
                    inclination_individual = ns[inclination_name]

                    g.add((inclination_individual, RDF.type, ns.Playstyle))
                    g.add(
                        (
                            inclination_individual,
                            ns.name,
                            Literal(city_state_data["inclination"]),
                        )
                    )
                    g.add(
                        (city_state_individual, ns.inclinedTo, inclination_individual)
                    )

                print(f"Processed city-state: {city_state_name}")
