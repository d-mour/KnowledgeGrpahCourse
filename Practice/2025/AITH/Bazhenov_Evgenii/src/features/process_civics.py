from bs4 import BeautifulSoup
import os
from rdflib import Graph, Namespace, Literal, RDF
import re


def parse_civic(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    try:
        name = (
            soup.find("div", class_="App_pageHeaderText__SsfWm").text.strip()
            if soup.find("div", class_="App_pageHeaderText__SsfWm")
            else None
        )

        historical_context_element = soup.find(
            string="Historical Context",
        )

        historical_context = (
            historical_context_element.parent.parent.nextSibling.text.strip()
            if historical_context_element
            else None
        )

        era_element = soup.find("p", class_="App_pageTabGroupText__SIZ8Y", string=True)
        era = era_element.text.strip() if era_element else None

        cost_element = soup.find(string="Research Cost")
        cost = (
            cost_element.parent.parent.find_next_sibling("div").text.strip()
            if cost_element and cost_element.parent
            else None
        )
        cost = int(re.findall(r"\d+", cost)[0]) if cost else None

        required_civics_element = soup.find(string="Required Civics")
        required_civics = (
            [
                link.text.strip()
                for link in required_civics_element.parent.parent.parent.find_all("a")
            ]
            if required_civics_element
            else []
        )

        leads_to_element = soup.find(string="Leads to Civics")
        leads_to = (
            [
                link.text.strip()
                for link in leads_to_element.parent.parent.parent.find_all("a")
            ]
            if leads_to_element
            else []
        )

        return {
            "name": name,
            "history": historical_context,
            "era": era,
            "cost": cost,
            "required_civics": required_civics,
            "leads_to_civics": leads_to,
        }
    except Exception as e:
        print(f"Error parsing civic: {e}")
        return None


def process_civics(folder_path, ns: Namespace, g: Graph):
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".html") or not file_name.startswith("civic_"):
            continue

        file_path = folder_path / file_name

        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
            civic_data = parse_civic(html_content)
            if civic_data:
                civic_name = civic_data["name"].strip().replace(" ", "_")
                civic_individual = ns[civic_name]

                g.add((civic_individual, RDF.type, ns.Civic))

                properties = {
                    ns.name: civic_data["name"],
                    ns.history: civic_data["history"],
                    ns.cost: civic_data["cost"],
                }
                for prop, value in properties.items():
                    if value:
                        g.add((civic_individual, prop, Literal(value)))

                if civic_data["era"]:
                    era_name = civic_data["era"].strip().replace(" ", "_")
                    era_individual = ns[era_name]

                    if (era_individual, None, None) not in g:
                        g.add((era_individual, RDF.type, ns.Era))
                        g.add((era_individual, ns.name, Literal(civic_data["era"])))

                    g.add((civic_individual, ns.unlocksIn, era_individual))

                for prereq in civic_data["required_civics"]:
                    prereq_individual = ns[prereq.replace(" ", "_")]

                    if (prereq_individual, None, None) not in g:
                        g.add((prereq_individual, RDF.type, ns.Technology))
                        g.add((prereq_individual, ns.name, Literal(prereq)))

                    g.add((civic_individual, ns.requires, prereq_individual))

                for leads_to in civic_data["leads_to_civics"]:
                    leads_to_individual = ns[leads_to.replace(" ", "_")]

                    if (leads_to_individual, None, None) not in g:
                        g.add((leads_to_individual, RDF.type, ns.Technology))
                        g.add((leads_to_individual, ns.name, Literal(leads_to)))

                    g.add((civic_individual, ns.leadsTo, leads_to_individual))

                print(f"Processed technology: {civic_name}")
