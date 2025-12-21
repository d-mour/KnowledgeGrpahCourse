from bs4 import BeautifulSoup
import os
from rdflib import Graph, Namespace, Literal, RDF


def parse_leader(html_content):
    """
    Parses the leader HTML content to extract relevant data.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    try:
        header = soup.find("div", class_="App_pageHeaderText__SsfWm")
        name = header.text.strip()

        civilization_element = soup.find(string="Civilizations")
        civilization = (
            soup.find(string="Traits")
            .parent.parent.find(string="Civilizations")
            .parent.parent.find_next_sibling()
            .text.strip()
            if civilization_element
            else "Unknown"
        )

        religion_element = soup.find(string="Preferences").parent.parent.find(
            string="Religion"
        )

        religion = (
            religion_element.parent.parent.find_next_sibling().text.strip()
            if religion_element
            else None
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
            "civilization": civilization,
            "religion": religion,
            "history": history,
            "unique_ability_name": unique_ability_name,
            "unique_ability_description": unique_ability_description,
        }
    except Exception as e:
        print(f"Error parsing leader: {e}")
        return None


def process_leaders(folder_path, ns: Namespace, g: Graph, replace=False):
    """
    Processes all civilization and leader HTML files
    in the specified folder and updates the ontology.
    """
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".html"):
            continue

        file_path = folder_path / file_name
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

            if file_name.startswith("leader_"):
                leader_data = parse_leader(html_content)

                if leader_data:
                    leader_name = leader_data["name"].strip().replace(" ", "_")
                    leader_individual = ns[leader_name]

                    if replace:
                        g.remove((leader_individual, None, None))

                    g.add((leader_individual, RDF.type, ns.Leader))
                    properties = {
                        ns.name: leader_data["name"],
                        ns.history: leader_data["history"],
                        ns.uniqueAbilityName: leader_data["unique_ability_name"],
                        ns.uniqueAbilityDescription: leader_data["unique_ability_name"],
                        ns.source: "civ6",
                    }
                    for prop, value in properties.items():
                        g.add((leader_individual, prop, Literal(value)))
                    print(f"Added leader {leader_name}")

                    civ_name = leader_data["civilization"].strip().replace(" ", "_")
                    civ_individual = ns[civ_name]
                    if leader_data["religion"]:
                        religion_name = leader_data["religion"]
                        religion_individual = ns[
                            religion_name.strip().replace(" ", "_")
                        ]
                        g.add((leader_individual, ns.believesIn, religion_individual))
                        print(f"Linked leader {leader_name} to religion {civ_name}")

                    g.add((leader_individual, ns.rules, civ_individual))
                    print(f"Linked leader {leader_name} to civilization {civ_name}")
