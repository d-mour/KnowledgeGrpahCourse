from bs4 import BeautifulSoup
import os
from rdflib import Graph, Namespace, Literal, RDF


def parse_civilization(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    try:
        name = soup.find("div", class_="App_pageHeaderText__SsfWm").text.strip()

        location_element = soup.find(string="Location")
        location = (
            location_element.parent.parent.nextSibling.text.strip()
            if location_element
            else "Unknown"
        )

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
            unique_ability_element.parent.parent.parent.nextSibling.next_element.find_all("p")[1].text.strip()
            if unique_ability_element
            else None
        )

        return {
            "name": name,
            "location": location,
            "history": history,
            "unique_ability_name": unique_ability_name,
            "unique_ability_description": unique_ability_description,
        }
    except Exception as e:
        print(f"Error parsing civilization: {e}")
        return None


def process_civilization(folder_path, ns: Namespace, g: Graph, replace=False):
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".html") or not file_name.startswith("civilization_"):
            continue

        file_path = folder_path / file_name
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
            civ_data = parse_civilization(html_content)

            if civ_data:
                civ_name = civ_data["name"].strip().replace(" ", "_")
                civ_individual = ns[civ_name]

                if replace:
                    g.remove((civ_individual, None, None))

                g.add((civ_individual, RDF.type, ns.Civilization))
                properties = {
                    ns.name: civ_data["name"],
                    ns.location: civ_data["location"],
                    ns.history: civ_data["history"],
                    ns.uniqueAbilityName: civ_data["unique_ability_name"],
                    ns.uniqueAbilityDescription: civ_data["unique_ability_name"],
                }
                for prop, value in properties.items():
                    g.add((civ_individual, prop, Literal(value)))
