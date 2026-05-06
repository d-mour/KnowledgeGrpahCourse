import json
from time import sleep
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF, OWL, RDFS
import urllib.parse

time_to_sleep_when_captcha = 5
country_map = {}
mode_map = {}
rank_map = {}


def normalize_name(name):
    """Заменяет пробелы и другие недопустимые символы для формирования корректного URI."""
    return urllib.parse.quote(name.replace(" ", "_"))


def p2f(x):
    return float(x.strip('%')) / 100


# Пространство имен
NS = Namespace("http://example.org/war_thunder#")

# Создаем граф
g = Graph()

# Открытие JSON
with open("../../recourse/final_eng.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Парсинг данных
aviation_class = URIRef(NS["aviation"])
ground_class = URIRef(NS["ground"])
country_class = URIRef(NS["country"])
mode_class = URIRef(NS["mode"])
rank_class = URIRef(NS["rank"])
g.add((aviation_class, RDF.type, RDFS.Class))
g.add((ground_class, RDF.type, RDFS.Class))
g.add((country_class, RDF.type, RDFS.Class))
g.add((mode_class, RDF.type, RDFS.Class))
g.add((rank_class, RDF.type, RDFS.Class))


def create_country(country):
    clazz = URIRef(NS[country])
    country_map[country] = clazz
    g.add((clazz, RDF.type, RDFS.Class))
    g.add((clazz, RDFS.subClassOf, country_class))


def create_mode(mode_prop):
    clazz = URIRef(NS[mode_prop])
    mode_map[mode_prop] = clazz
    g.add((clazz, RDF.type, RDFS.Class))
    g.add((clazz, RDFS.subClassOf, mode_class))


def create_rank(rank):
    clazz = URIRef(NS[rank])
    rank_map[rank] = clazz
    g.add((clazz, RDF.type, RDFS.Class))
    g.add((clazz, RDFS.subClassOf, rank_class))


for aircraft_type, aircraft_list in data["aviation"].items():
    aircraft_type_class = URIRef(NS[aircraft_type.replace(" ", "_")])
    g.add((aircraft_type_class, RDF.type, RDFS.Class))
    g.add((aircraft_type_class, RDFS.subClassOf, aviation_class))
    g.add((aviation_class, NS.hasType, aircraft_type_class))

    for aircraft in aircraft_list:
        # Создание индивидуала для самолета
        aircraft_individual = URIRef(NS[normalize_name(aircraft["name"])])
        g.add((aircraft_individual, RDF.type, aircraft_type_class))
        g.add((aircraft_individual, RDF.type, OWL.NamedIndividual))
        types = aircraft["type"].split(' / ')
        for t in types:
            g.add((aircraft_individual, NS.hasType, URIRef(NS[t.replace(" ", "_")])))

        if country_map.__contains__(aircraft["country"].lower()):
            g.add((aircraft_individual, NS.hasCountry, country_map.get(aircraft["country"].lower())))
        else:
            create_country(aircraft["country"].lower())
            g.add((aircraft_individual, NS.hasCountry, country_map.get(aircraft["country"].lower())))

        if rank_map.__contains__(aircraft['rank']):
            g.add((aircraft_individual, NS.hasRank, rank_map.get(aircraft['rank'])))
        else:
            create_rank(aircraft['rank'])
            g.add((aircraft_individual, NS.hasRank, rank_map.get(aircraft['rank'])))

        g.add((aircraft_individual, NS.hasPrice, URIRef(NS[aircraft["price"].replace(' SL', '')])))

        # Парсинг режимов
        for mode, mode_data in aircraft["modes"].items():
            if not mode_map.__contains__(mode):
                create_mode(mode)

            mode_concrete_class = mode_map.get(mode)
            mode_individual = URIRef(NS[f"{normalize_name(aircraft['name'])}_{mode}"])
            g.add((mode_individual, RDF.type, mode_concrete_class))
            g.add((mode_individual, RDF.type, OWL.NamedIndividual))
            g.add((aircraft_individual, NS.hasMode, mode_individual))

            # Парсинг статистики, бонусов и ремонта
            for category, props in mode_data.items():
                category_class = URIRef(NS[category])
                category_individual = URIRef(NS[f"{normalize_name(aircraft['name'])}_{mode}_{category}"])
                g.add((category_individual, RDF.type, category_class))
                g.add((category_individual, RDF.type, OWL.NamedIndividual))
                g.add((mode_individual, NS[f"has{category.capitalize()}"], category_individual))

                # Добавление свойств
                for key, value in props.items():
                    if value is None:
                        value = "0"  # Заменяем null на 0
                    if key == 'win_rate' or key == 'silverLionBonus' or key == 'expBonus':
                        g.add((category_individual, NS[key], URIRef(NS[str(p2f(value))])))
                    elif key == 'repairCost' or key == 'repairCostPerMinute' or key == 'repairFullCost':
                        g.add((category_individual, NS[key], URIRef(NS[value.replace(' SL', '')])))
                    else:
                        g.add((category_individual, NS[key], URIRef(NS[str(value)])))

for ground_type, ground_list in data["ground"].items():
    ground_type_class = URIRef(NS[ground_type.replace(" ", "_")])
    g.add((ground_type_class, RDF.type, RDFS.Class))
    g.add((ground_type_class, RDFS.subClassOf, ground_class))
    g.add((ground_class, NS.hasType, ground_type_class))

    for ground in ground_list:
        # Создание индивидуала для самолета
        ground_individual = URIRef(NS[normalize_name(ground["name"])])
        g.add((ground_individual, RDF.type, ground_type_class))
        g.add((ground_individual, RDF.type, OWL.NamedIndividual))
        types = ground["type"].split(' / ')
        for t in types:
            g.add((ground_individual, NS.hasType, URIRef(NS[t.replace(" ", "_")])))

        if country_map.__contains__(ground["country"].lower()):
            g.add((ground_individual, NS.hasCountry, country_map.get(ground["country"].lower())))
        else:
            create_country(ground["country"].lower())
            g.add((ground_individual, NS.hasCountry, country_map.get(ground["country"].lower())))

        if rank_map.__contains__(ground['rank']):
            g.add((ground_individual, NS.hasRank, rank_map.get(ground['rank'])))
        else:
            create_rank(ground['rank'])
            g.add((ground_individual, NS.hasRank, rank_map.get(ground['rank'])))

        g.add((ground_individual, NS.hasPrice, URIRef(NS[ground["price"].replace(' SL', '')])))

        # Парсинг режимов
        for mode, mode_data in ground["modes"].items():
            if not mode_map.__contains__(mode):
                create_mode(mode)

            mode_concrete_class = mode_map.get(mode)
            mode_individual = URIRef(NS[f"{normalize_name(ground['name'])}_{mode}"])
            g.add((mode_individual, RDF.type, mode_concrete_class))
            g.add((mode_individual, RDF.type, OWL.NamedIndividual))
            g.add((ground_individual, NS.hasMode, mode_individual))

            # Парсинг статистики, бонусов и ремонта
            for category, props in mode_data.items():
                category_class = URIRef(NS[category])
                category_individual = URIRef(NS[f"{normalize_name(ground['name'])}_{mode}_{category}"])
                g.add((category_individual, RDF.type, category_class))
                g.add((category_individual, RDF.type, OWL.NamedIndividual))
                g.add((mode_individual, NS[f"has{category.capitalize()}"], category_individual))

                # Добавление свойств
                for key, value in props.items():
                    if value is None:
                        value = "0"  # Заменяем null на 0
                    if key == 'win_rate' or key == 'silverLionBonus' or key == 'expBonus':
                        g.add((category_individual, NS[key], URIRef(NS[str(p2f(value))])))
                    elif key == 'repairCost' or key == 'repairCostPerMinute' or key == 'repairFullCost':
                        g.add((category_individual, NS[key], URIRef(NS[value.replace(' SL', '')])))
                    else:
                        g.add((category_individual, NS[key], URIRef(NS[str(value)])))


try:
    # Сохраняем в файл Turtle
    with open("aviation.ttl", "w", encoding="utf-8") as ttl_file:
        ttl_file.write(g.serialize(format="turtle"))
except:
    sleep(time_to_sleep_when_captcha)
    time_to_sleep_when_captcha += 5
