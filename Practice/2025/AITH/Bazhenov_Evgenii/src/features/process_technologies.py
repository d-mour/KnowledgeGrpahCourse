from bs4 import BeautifulSoup
import os
from rdflib import Graph, Namespace, Literal, RDF
import re


def parse_technology(html_content):
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
        cost = int(re.findall(r"\d+", cost)[0])

        required_techs_element = soup.find(string="Required Technologies")
        required_techs = (
            [
                link.text.strip()
                for link in required_techs_element.parent.parent.parent.find_all("a")
            ]
            if required_techs_element
            else []
        )

        leads_to_element = soup.find(string="Leads to Technologies")
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
            "required_technologies": required_techs,
            "leads_to_technologies": leads_to,
        }
    except Exception as e:
        print(f"Error parsing technology: {e}")
        return None


def process_technologies(folder_path, ns: Namespace, g: Graph):
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".html") or not file_name.startswith("tech_"):
            continue

        file_path = folder_path / file_name

        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
            technology_data = parse_technology(html_content)

            if technology_data:
                tech_name = technology_data["name"].strip().replace(" ", "_")
                tech_individual = ns[tech_name]

                g.add((tech_individual, RDF.type, ns.Technology))

                properties = {
                    ns.name: technology_data["name"],
                    ns.history: technology_data["history"],
                    ns.cost: technology_data["cost"],
                }
                for prop, value in properties.items():
                    if value:
                        g.add((tech_individual, prop, Literal(value)))

                if technology_data["era"]:
                    era_name = technology_data["era"].strip().replace(" ", "_")
                    era_individual = ns[era_name]

                    if (era_individual, None, None) not in g:
                        g.add((era_individual, RDF.type, ns.Era))
                        g.add(
                            (era_individual, ns.name, Literal(technology_data["era"]))
                        )

                    g.add((tech_individual, ns.unlocksIn, era_individual))

                for prereq in technology_data["required_technologies"]:
                    prereq_individual = ns[prereq.replace(" ", "_")]

                    g.add((prereq_individual, RDF.type, ns.Technology))
                    g.add((prereq_individual, ns.name, Literal(prereq)))

                    g.add((tech_individual, ns.requires, prereq_individual))

                for leads_to in technology_data["leads_to_technologies"]:
                    leads_to_individual = ns[leads_to.replace(" ", "_")]

                    g.add((leads_to_individual, RDF.type, ns.Technology))
                    g.add((leads_to_individual, ns.name, Literal(leads_to)))

                    g.add((tech_individual, ns.leadsTo, leads_to_individual))

                print(f"Processed technology: {tech_name}")
