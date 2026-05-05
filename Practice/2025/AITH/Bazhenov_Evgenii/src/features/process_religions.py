from bs4 import BeautifulSoup
import os
from rdflib import Graph, Namespace, Literal, RDF


def parse_religion(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    try:
        header = soup.find("div", class_="App_pageHeaderText__SsfWm")
        name = header.text.strip()

        return {"name": name}
    except Exception as e:
        print(f"Error parsing religion: {e}")
        return None


def process_religions(folder_path, ns: Namespace, g: Graph, replace=False):
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".html"):
            continue

        file_path = folder_path / file_name
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

            if file_name.startswith("religion_"):
                religion_data = parse_religion(html_content)

                if religion_data:
                    religion_name = religion_data["name"].strip().replace(" ", "_")
                    religion_individual = ns[religion_name]

                    if replace:
                        g.remove((religion_individual, None, None))

                    g.add((religion_individual, RDF.type, ns.Religion))
                    properties = {
                        ns.name: religion_data["name"],
                    }
                    for prop, value in properties.items():
                        g.add((religion_individual, prop, Literal(value)))
                    print(f"Added {religion_data["name"]} religion")
