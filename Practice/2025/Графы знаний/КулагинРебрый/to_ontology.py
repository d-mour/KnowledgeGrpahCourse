import json
import re
import os
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef, BNode
from rdflib.namespace import OWL, XSD
import uuid






FILES = {
    "leaders": "civ6_leader_bonuses.json",
    "civs": "civ6_civilization_bonuses.json",
    "infrastructure": "infrastructure_data.json",
    "traits": "civ6_leaders_victory_traits.json",
    "links": "leader_to_civilization_map.json"
}


INPUT_ONTOLOGY = "onto-v3.rdf"
OUTPUT_ONTOLOGY = "onto-v3.rdf_final_final.owl"


BASE_IRI = "http://www.semanticweb.org/kulag/ontologies/2025/9/civ6-knowledge-base/"
KB = Namespace(BASE_IRI + "#")


KNOWN_DISTRICTS = {
    "Acropolis", "Bath", "Cothon", "Hippodrome", "Hansa", "Ikanda", "Lavra",
    "Mbanza", "Oppidum", "Seowon", "Street Carnival", "Suguba", "Thành", "Tsikhe",
    "Royal Navy Dockyard", "Holy Site", "Campus", "Encampment", "Theater Square",
    "Commercial Hub", "Industrial Zone", "Harbor", "Aerodrome", "Aqueduct",
    "Neighborhood", "Canal", "Dam", "Preserve", "Spaceport", "Government Plaza",
    "Diplomatic Quarter", "Water Park", "Observatory", "Than", "Mbiza"
}

YIELD_MAP = {
    "culture": KB.Culture, "faith": KB.Faith, "food": KB.Food, "gold": KB.Gold,
    "production": KB.Production, "science": KB.Science, "tourism": KB.Tourism,
    "amenity": KB.Amenity, "amenities": KB.Amenity, "diplomatic favor": KB.DiplomaticFavor,
    "housing": KB.Food
}

VICTORY_KEYWORDS = {
    "CULTURAL": KB.CultureVictory, "CULTURE": KB.CultureVictory,
    "RELIGIOUS": KB.ReligiousVictory, "RELIGION": KB.ReligiousVictory,
    "SCIENCE": KB.ScienceVictory,
    "AGGRESSIVE": KB.DominationVictory, "DOMINATION": KB.DominationVictory, "EXPANSIONIST": KB.DominationVictory,
    "DIPLOMATIC": KB.DiplomaticVictory
}






def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка чтения {filename}: {e}")
    else:
        print(f"Файл {filename} не найден, пропускаем.")
    return []


def clean_uri(text):
    """Очистка строки для создания валидного URI"""
    if not text: return "Unknown"
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text).strip()
    return text.replace(" ", "_")


def get_base_name_for_search(name):
    """
    Упрощает имя для поиска: 'Saladin (Vizier)' -> 'SALADIN'
    Нужно для связывания traits.json с leaders.json
    """
    if not name: return ""
    name = re.sub(r'\(.*?\)', '', name)
    return name.strip().upper()


def normalize_trait_id(leader_id):
    """
    Упрощает ID трейта: 'LEADER_SALADIN_ALT' -> 'SALADIN'
    """
    name = leader_id.replace("LEADER_", "")

    if "T_ROOSEVELT" in name: name = name.replace("T_ROOSEVELT", "TEDDY_ROOSEVELT")
    if "PETER_GREAT" in name: name = "PETER"
    if "QIN" == name: name = "QIN SHI HUANG"

    name = name.replace("_ALT", "").replace("_NULL", "")
    name = name.replace("_", " ")
    return name.strip().upper()


def get_strength_level(value):
    """Число -> Уровень силы (URI)"""
    try:
        val = float(value)
        if val >= 4:
            return KB.High
        elif val >= 2:
            return KB.Medium
        else:
            return KB.Low
    except ValueError:
        return KB.Low


def parse_text_for_yields(text):
    """Парсинг текста на ресурсы и силу. Возвращает [(YieldURI, StrengthURI)]"""
    found = []
    text_lower = text.lower()

    pattern = re.compile(
        r'\+?(\d+(?:\.\d+)?)\s+(culture|faith|food|gold|production|science|tourism|amenity|amenities|diplomatic favor)')
    matches = pattern.findall(text_lower)

    for amount, yield_name in matches:
        y_uri = YIELD_MAP.get(yield_name)
        if y_uri:
            found.append((y_uri, get_strength_level(amount)))


    if not found:
        for word, uri in YIELD_MAP.items():
            if word in text_lower and " adjacent " not in text_lower:
                found.append((uri, KB.Low))
    return found


def define_ontology_schema(g):
    """
    Явно прописываем типы свойств, чтобы Protégé не считал их аннотациями.
    """

    ops = [
        KB.hasLeader, KB.hasAbility, KB.hasStructure, KB.hasYieldAffection,
        KB.affectYield, KB.hasAffinity, KB.hasAffinityDetail, KB.targetsVictory,
        KB.hasStrength, KB.hasVictoryAffection, KB.affectVictory, KB.enhances
    ]
    for p in ops: g.add((p, RDF.type, OWL.ObjectProperty))


    dps = [KB.hasName, KB.hasDescription, KB.bonusType]
    for p in dps: g.add((p, RDF.type, OWL.DatatypeProperty))


    classes = [
        KB.Leader, KB.Civilization, KB.Ability, KB.Structure, KB.Building,
        KB.District, KB.Yield, KB.VictoryType, KB.VictoryAffinity, KB.YieldAffection
    ]
    for c in classes: g.add((c, RDF.type, OWL.Class))






def main():
    print("--- Начинаем сборку Графа Знаний ---")
    g = Graph()


    try:
        g.parse(INPUT_ONTOLOGY, format="xml")
        print(f"Онтология загружена: {len(g)} триплетов.")
    except FileNotFoundError:
        print("Файл онтологии не найден. Создаем с нуля.")

    g.bind("civ6", KB)
    g.bind("owl", OWL)


    define_ontology_schema(g)


    leader_lookup = {}
    civ_lookup = {}


    leaders_data = load_json(FILES["leaders"])
    print(f"Обработка лидеров ({len(leaders_data)})...")

    for item in leaders_data:
        l_name = item.get("leader_name")
        if not l_name: continue

        l_uri = KB[clean_uri(l_name)]
        ab_uri = KB[clean_uri(item.get("bonus_name"))]
        desc = item.get("bonus_description", "")


        leader_lookup[l_name] = l_uri
        leader_lookup[get_base_name_for_search(l_name)] = l_uri


        g.add((l_uri, RDF.type, KB.Leader))
        g.add((l_uri, RDF.type, OWL.NamedIndividual))
        g.add((l_uri, KB.hasName, Literal(l_name, datatype=XSD.string)))

        g.add((ab_uri, RDF.type, KB.Ability))
        g.add((ab_uri, RDF.type, OWL.NamedIndividual))
        g.add((ab_uri, KB.hasName, Literal(item.get("bonus_name"), datatype=XSD.string)))
        g.add((ab_uri, KB.hasDescription, Literal(desc, datatype=XSD.string)))

        g.add((l_uri, KB.hasAbility, ab_uri))


        for y_uri, str_uri in parse_text_for_yields(desc):
            aff_node = KB[f"Bonus_{uuid.uuid4().hex[:8]}"]
            g.add((aff_node, RDF.type, KB.YieldAffection))
            g.add((ab_uri, KB.hasYieldAffection, aff_node))
            g.add((aff_node, KB.affectYield, y_uri))
            g.add((aff_node, KB.hasStrength, str_uri))


    civs_data = load_json(FILES["civs"])
    print(f"Обработка цивилизаций ({len(civs_data)})...")

    for item in civs_data:
        c_name = item.get("civilization_name")
        c_uri = KB[clean_uri(c_name)]
        ab_uri = KB[clean_uri(item.get("ability_name"))]
        desc = item.get("ability_description", "")

        civ_lookup[c_name] = c_uri

        g.add((c_uri, RDF.type, KB.Civilization))
        g.add((c_uri, RDF.type, OWL.NamedIndividual))
        g.add((c_uri, KB.hasName, Literal(c_name, datatype=XSD.string)))

        g.add((ab_uri, RDF.type, KB.Ability))
        g.add((ab_uri, RDF.type, OWL.NamedIndividual))
        g.add((ab_uri, KB.hasName, Literal(item.get("ability_name"), datatype=XSD.string)))
        g.add((ab_uri, KB.hasDescription, Literal(desc, datatype=XSD.string)))

        g.add((c_uri, KB.hasAbility, ab_uri))


    links_data = load_json(FILES["links"])
    print(f"Обработка связей...")
    for link in links_data:
        l_uri = leader_lookup.get(link.get("leader"))
        c_uri = civ_lookup.get(link.get("civilization"))

        if l_uri and c_uri:
            g.add((c_uri, KB.hasLeader, l_uri))


    infra_data = load_json(FILES["infrastructure"])
    processed_structs = set()
    print(f"Обработка инфраструктуры ({len(infra_data)})...")

    for item in infra_data:
        l_name = item.get("leader_name")
        s_name = item.get("infrastructure_name")
        effects = item.get("effects", [])

        s_key = clean_uri(s_name)
        s_uri = KB[s_key]


        if s_key not in processed_structs:

            sType = KB.District if s_name.split('(')[0].strip() in KNOWN_DISTRICTS else KB.Building

            g.add((s_uri, RDF.type, sType))
            g.add((s_uri, RDF.type, OWL.NamedIndividual))
            g.add((s_uri, KB.hasName, Literal(s_name, datatype=XSD.string)))
            g.add((s_uri, KB.hasDescription, Literal(" ".join(effects), datatype=XSD.string)))


            for line in effects:
                for y_uri, str_uri in parse_text_for_yields(line):
                    aff_node = BNode()
                    g.add((aff_node, RDF.type, KB.YieldAffection))
                    g.add((s_uri, KB.hasYieldAffection, aff_node))
                    g.add((aff_node, KB.affectYield, y_uri))
                    g.add((aff_node, KB.hasStrength, str_uri))

            processed_structs.add(s_key)


        l_uri = leader_lookup.get(l_name)
        if l_uri:

            found_civ = None
            for s, p, o in g.triples((None, KB.hasLeader, l_uri)):
                found_civ = s
                break

            if found_civ:
                g.add((found_civ, KB.hasStructure, s_uri))
            else:

                g.add((l_uri, KB.hasStructure, s_uri))


    traits_data = load_json(FILES["traits"])
    count_traits = 0
    print(f"Обработка трейтов ({len(traits_data)})...")

    for item in traits_data:
        raw_id = item.get("leader", "")
        traits = item.get("traits", [])

        target_name = normalize_trait_id(raw_id)

        l_uri = None

        if target_name in leader_lookup:
            l_uri = leader_lookup[target_name]
        else:

            for key, uri in leader_lookup.items():
                if target_name in key or key in target_name:
                    l_uri = uri
                    break

        if l_uri:
            for trait in traits:
                for key, vic_uri in VICTORY_KEYWORDS.items():
                    if key in trait:

                        str_uri = KB.High if ("MAJOR" in trait or "AGGRESSIVE" in trait) else KB.Medium
                        if "LOW" in trait: str_uri = KB.Low


                        aff_node = BNode()
                        g.add((aff_node, RDF.type, KB.LeaderVictoryAffinity))
                        g.add((l_uri, KB.hasAffinityDetail, aff_node))
                        g.add((aff_node, KB.targetsVictory, vic_uri))
                        g.add((aff_node, KB.hasStrength, str_uri))


                        g.add((vic_uri, RDF.type, KB.VictoryType))
                        g.add((vic_uri, RDF.type, OWL.NamedIndividual))
                        count_traits += 1
                        break

    print(f"Связано трейтов с лидерами: {count_traits}")


    g.serialize(destination=OUTPUT_ONTOLOGY, format="xml")
    print(f"--- ГОТОВО! ---")
    print(f"Файл сохранен: {OUTPUT_ONTOLOGY}")
    print(f"Всего триплетов: {len(g)}")


if __name__ == "__main__":
    main()