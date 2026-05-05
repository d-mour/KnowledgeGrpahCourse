# -*- coding: utf-8 -*-
import os
import re
import csv
from rdflib import Graph, URIRef, Literal, RDF, XSD

# === ПУТИ К ФАЙЛАМ ===
TTL_INPUT = "cs2_ontology_full.ttl"         # исходная онтология
CSV_INPUT = "cs2_data_1000.csv"             # CSV-файл с данными
TTL_OUTPUT = "cs2_ontology_full_updated_1.ttl"  # итоговая онтология

# === НАСТРОЙКИ ===
BASE_NS = "http://example.org/cs2#"  # базовое пространство имён

# === УТИЛИТЫ ===
def make_safe_uri(local_id: str) -> URIRef:
    safe_local = re.sub(r"[^a-zA-Z0-9_\-]", "_", local_id.strip())
    return URIRef(BASE_NS + safe_local)

def add_literal_typed(graph, subj, prop_uri, value, dtype=None):
    if value is None or str(value).strip() == "":
        return
    if dtype:
        graph.add((subj, URIRef(prop_uri), Literal(value, datatype=dtype)))
    else:
        graph.add((subj, URIRef(prop_uri), Literal(value)))

def add_individual(graph, row):
    raw_id = row.get("id") or f"anon_{hash(str(row)) & 0xffff}"
    subj = make_safe_uri(raw_id)

    # rdf:type (класс)
    if row.get("class"):
        try:
            graph.add((subj, RDF.type, URIRef(row["class"])))
        except Exception:
            graph.add((subj, RDF.type, Literal(row["class"])))

    # === СВОЙСТВА ===
    # текстовые
    add_literal_typed(graph, subj, "http://xmlns.com/foaf/0.1/name", row.get("name"))
    add_literal_typed(graph, subj, BASE_NS + "rarity", row.get("rarity"))
    add_literal_typed(graph, subj, BASE_NS + "collection", row.get("collection"))
    add_literal_typed(graph, subj, BASE_NS + "wear_condition", row.get("wear_condition"))

    # числовые (decimal)
    add_literal_typed(graph, subj, BASE_NS + "price_usd", row.get("price_usd"), XSD.decimal)
    add_literal_typed(graph, subj, BASE_NS + "profit_usd", row.get("profit_usd"), XSD.decimal)
    add_literal_typed(graph, subj, BASE_NS + "float_value", row.get("float_value"), XSD.decimal)
    add_literal_typed(graph, subj, BASE_NS + "sticker_count", row.get("sticker_count"), XSD.integer)

    # дата
    add_literal_typed(graph, subj, BASE_NS + "date", row.get("date"), XSD.date)

    # булевые (строка → boolean)
    for prop in ["is_stattrak", "is_souvenir"]:
        val = str(row.get(prop)).strip().lower()
        if val in ("true", "1", "yes"):
            add_literal_typed(graph, subj, BASE_NS + prop, True, XSD.boolean)
        elif val in ("false", "0", "no"):
            add_literal_typed(graph, subj, BASE_NS + prop, False, XSD.boolean)

    # ссылки (URI)
    for prop, col in [("owner", "owner"), ("transaction_type", "transaction_type")]:
        val = row.get(col)
        if val:
            obj = URIRef(val) if val.startswith("http") else make_safe_uri(val)
            graph.add((subj, URIRef(BASE_NS + prop), obj))

    return subj

# === ЗАГРУЗКА ОНТОЛОГИИ ===
if not os.path.exists(TTL_INPUT):
    raise FileNotFoundError(f"❌ Не найден файл онтологии: {TTL_INPUT}")
if not os.path.exists(CSV_INPUT):
    raise FileNotFoundError(f"❌ Не найден CSV: {CSV_INPUT}")

g = Graph()
g.parse(TTL_INPUT, format="turtle")
print(f"✅ Загружена онтология: {TTL_INPUT}")
print(f"🔹 Тройк до добавления: {len(g)}")

# === ДОБАВЛЕНИЕ ИНДИВИДОВ ===
added = 0
examples = []

with open(CSV_INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        subj = add_individual(g, row)
        added += 1
        if i < 5:
            examples.append((row["id"], subj))

print(f"✅ Добавлено {added} индивидов из CSV")

# === СОХРАНЕНИЕ ===
g.serialize(destination=TTL_OUTPUT, format="turtle")
print(f"💾 Сохранено в файл: {TTL_OUTPUT}")
print(f"🔢 Итоговое количество троек: {len(g)}")

print("\nПримеры добавленных URI:")
for rid, uri in examples:
    print(f"  {rid}  ->  {uri}")
