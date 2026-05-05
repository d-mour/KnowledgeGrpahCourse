import json
import re
from pathlib import Path

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD

# 1. Пути к файлам

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "combined_fraud_ads_annotations.json"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

TTL_PATH = OUTPUT_DIR / "fraud_ads_graph.ttl"
RDF_PATH = OUTPUT_DIR / "fraud_ads_graph.rdf"
SPARQL_RESULTS_PATH = OUTPUT_DIR / "sparql_results.txt"


# 2. Пространство имен RDF

EX = Namespace("http://example.org/fraud-ads/")

# 3. Вспомогательные функции

def safe_id(value: str) -> str:
    """
    Преобразует строку в безопасный идентификатор для URI.

    Например:
    "ad_001 ready ООО" -> "ad_001_ready_ооо"
    """
    value = str(value).strip().lower()
    value = value.replace("ё", "е")
    value = re.sub(r"[^a-zа-я0-9_]+", "_", value, flags=re.IGNORECASE)
    value = re.sub(r"_+", "_", value).strip("_")

    return value or "empty"


def add_literal(g: Graph, subject, predicate, value, datatype=None):
    """
    Добавляет литерал в RDF-граф, если значение не пустое.
    """
    if value is None or value == "":
        return

    if datatype:
        g.add((subject, predicate, Literal(value, datatype=datatype)))
    else:
        g.add((subject, predicate, Literal(value)))


def add_ontology(g: Graph):
    """
    Добавляет минимальную онтологию:
    классы и свойства предметной области.
    """

    classes = [
        "Dataset",
        "Advertisement",

        "TextAnnotation",
        "Token",
        "LemmaPair",
        "POSTag",
        "Phrase",
        "Dependency",
        "NamedEntity",
        "Sentiment",

        "ImageAnnotation",
        "Region",
        "VisualObject",
        "VisualAttribute",
        "ColorFeature",
        "OCRText",

        "Signal"
    ]

    for class_name in classes:
        g.add((EX[class_name], RDF.type, RDFS.Class))

    properties = [
        "hasAd",
        "hasTitle",
        "hasLabel",

        "hasTextAnnotation",
        "hasImageAnnotation",

        "hasToken",
        "tokenValue",

        "hasLemmaPair",
        "lemmaToken",
        "lemmaValue",

        "hasPOSTag",
        "posToken",
        "posValue",

        "syntaxStructure",
        "hasPhrase",
        "phraseType",
        "phraseText",

        "hasDependency",
        "dependencyToken",
        "dependencyRelation",
        "dependencyHead",

        "hasNamedEntity",
        "entityText",
        "entityType",

        "hasSentiment",
        "sentimentScore",
        "sentimentLabel",

        "hasRegion",
        "regionId",
        "regionType",
        "position",
        "bboxX",
        "bboxY",
        "bboxWidth",
        "bboxHeight",

        "hasVisualObject",
        "objectId",
        "objectName",
        "objectClass",
        "belongsToRegion",

        "hasVisualAttribute",
        "attributeObjectId",
        "attributeName",
        "attributeValue",

        "hasColorFeature",
        "colorName",
        "colorIntensity",
        "colorRole",
        "contrast",
        "brightness",
        "saturation",

        "layout",
        "focusArea",
        "hasSpatialRelation",
        "relationFrom",
        "relationType",
        "relationTo",

        "hasOCRText",
        "ocrText",
        "ocrConfidence",

        "sceneType",
        "domain",
        "message",

        "hasSignal",
        "signalText",
        "signalCategory",

        "description",
        "comment",
        "riskLevel",
        "classificationComment"
    ]

    for prop_name in properties:
        g.add((EX[prop_name], RDF.type, RDF.Property))


# 4. Текстовая модальность

def add_text_annotation(g: Graph, ad_uri, ad_id: str, text_data: dict):
    """
    Добавляет в RDF-граф текстовую разметку объявления.
    """

    text_uri = EX[f"{safe_id(ad_id)}_text"]

    g.add((text_uri, RDF.type, EX.TextAnnotation))
    g.add((ad_uri, EX.hasTextAnnotation, text_uri))

    # Уровень разметки
    level_info = text_data.get("Уровень разметки", {})
    add_literal(g, text_uri, EX.description, level_info.get("description"))

    # Токенизация
    tokens = text_data.get("Токенизация", {}).get("tokens", [])

    for i, token in enumerate(tokens, start=1):
        token_uri = EX[f"{safe_id(ad_id)}_token_{i}"]

        g.add((token_uri, RDF.type, EX.Token))
        g.add((token_uri, EX.tokenValue, Literal(token)))
        g.add((text_uri, EX.hasToken, token_uri))

    # Лемматизация
    lemmas = text_data.get("Лемматизация", {}).get("lemmas", [])

    for i, item in enumerate(lemmas, start=1):
        lemma_uri = EX[f"{safe_id(ad_id)}_lemma_{i}"]

        g.add((lemma_uri, RDF.type, EX.LemmaPair))
        add_literal(g, lemma_uri, EX.lemmaToken, item.get("token"))
        add_literal(g, lemma_uri, EX.lemmaValue, item.get("lemma"))

        g.add((text_uri, EX.hasLemmaPair, lemma_uri))

    # POS-теггинг
    pos_tags = text_data.get("POS-теггинг", {}).get("pos_tags", [])

    for i, item in enumerate(pos_tags, start=1):
        pos_uri = EX[f"{safe_id(ad_id)}_pos_{i}"]

        g.add((pos_uri, RDF.type, EX.POSTag))
        add_literal(g, pos_uri, EX.posToken, item.get("token"))
        add_literal(g, pos_uri, EX.posValue, item.get("pos"))

        g.add((text_uri, EX.hasPOSTag, pos_uri))

    # Синтаксический анализ
    syntax = text_data.get("Синтаксический анализ", {})

    add_literal(g, text_uri, EX.syntaxStructure, syntax.get("structure"))
    add_literal(g, text_uri, EX.comment, syntax.get("comment"))

    phrases = syntax.get("phrases", [])

    for i, item in enumerate(phrases, start=1):
        phrase_uri = EX[f"{safe_id(ad_id)}_phrase_{i}"]

        g.add((phrase_uri, RDF.type, EX.Phrase))
        add_literal(g, phrase_uri, EX.phraseType, item.get("type"))
        add_literal(g, phrase_uri, EX.phraseText, item.get("text"))

        g.add((text_uri, EX.hasPhrase, phrase_uri))

    # Зависимости
    dependencies = text_data.get("Зависимости", {}).get("dependencies", [])

    for i, item in enumerate(dependencies, start=1):
        dep_uri = EX[f"{safe_id(ad_id)}_dependency_{i}"]

        g.add((dep_uri, RDF.type, EX.Dependency))
        add_literal(g, dep_uri, EX.dependencyToken, item.get("token"))
        add_literal(g, dep_uri, EX.dependencyRelation, item.get("relation"))
        add_literal(g, dep_uri, EX.dependencyHead, item.get("head"))

        g.add((text_uri, EX.hasDependency, dep_uri))

    # NER
    entities = text_data.get("NER", {}).get("entities", [])

    for i, item in enumerate(entities, start=1):
        entity_uri = EX[f"{safe_id(ad_id)}_entity_{i}"]

        g.add((entity_uri, RDF.type, EX.NamedEntity))
        add_literal(g, entity_uri, EX.entityText, item.get("text"))
        add_literal(g, entity_uri, EX.entityType, item.get("type"))

        g.add((text_uri, EX.hasNamedEntity, entity_uri))

    # Сентимент
    sentiment = text_data.get("Сентимент", {})

    sentiment_uri = EX[f"{safe_id(ad_id)}_text_sentiment"]

    g.add((sentiment_uri, RDF.type, EX.Sentiment))
    add_literal(g, sentiment_uri, EX.sentimentScore, sentiment.get("score"), XSD.float)
    add_literal(g, sentiment_uri, EX.sentimentLabel, sentiment.get("label"))
    add_literal(g, sentiment_uri, EX.comment, sentiment.get("comment"))

    g.add((text_uri, EX.hasSentiment, sentiment_uri))

    # Дополнительные признаки: fraud_signals, legit_like_signals
    extra = text_data.get("Дополнительные признаки", {})

    add_literal(g, text_uri, EX.riskLevel, extra.get("risk_level"))
    add_literal(g, text_uri, EX.classificationComment, extra.get("classification_comment"))

    for category in ["fraud_signals", "legit_like_signals"]:
        signals = extra.get(category, [])

        for i, signal_text in enumerate(signals, start=1):
            signal_uri = EX[f"{safe_id(ad_id)}_text_{safe_id(category)}_{i}"]

            g.add((signal_uri, RDF.type, EX.Signal))
            g.add((signal_uri, EX.signalText, Literal(signal_text)))
            g.add((signal_uri, EX.signalCategory, Literal(category)))

            g.add((text_uri, EX.hasSignal, signal_uri))


# 5. Визуальная модальность


def add_image_annotation(g: Graph, ad_uri, ad_id: str, image_data: dict):
    """
    Добавляет в RDF-граф визуальную разметку объявления.
    """

    image_uri = EX[f"{safe_id(ad_id)}_image"]

    g.add((image_uri, RDF.type, EX.ImageAnnotation))
    g.add((ad_uri, EX.hasImageAnnotation, image_uri))

    # Уровень разметки
    level_info = image_data.get("Уровень разметки", {})
    add_literal(g, image_uri, EX.description, level_info.get("description"))

    # Области изображения
    regions = image_data.get("Области изображения", {}).get("regions", [])

    for region in regions:
        region_id = region.get("region_id", "")
        region_uri = EX[f"{safe_id(ad_id)}_region_{safe_id(region_id)}"]

        g.add((region_uri, RDF.type, EX.Region))
        add_literal(g, region_uri, EX.regionId, region_id)
        add_literal(g, region_uri, EX.regionType, region.get("type"))
        add_literal(g, region_uri, EX.position, region.get("position"))
        add_literal(g, region_uri, EX.description, region.get("description"))

        bbox = region.get("bbox", {})

        add_literal(g, region_uri, EX.bboxX, bbox.get("x"), XSD.integer)
        add_literal(g, region_uri, EX.bboxY, bbox.get("y"), XSD.integer)
        add_literal(g, region_uri, EX.bboxWidth, bbox.get("width"), XSD.integer)
        add_literal(g, region_uri, EX.bboxHeight, bbox.get("height"), XSD.integer)

        g.add((image_uri, EX.hasRegion, region_uri))

    # Объекты изображения
    objects = image_data.get("Объекты", {}).get("objects", [])

    for obj in objects:
        object_id = obj.get("object_id", "")
        object_uri = EX[f"{safe_id(ad_id)}_object_{safe_id(object_id)}"]

        g.add((object_uri, RDF.type, EX.VisualObject))
        add_literal(g, object_uri, EX.objectId, object_id)
        add_literal(g, object_uri, EX.objectName, obj.get("name"))
        add_literal(g, object_uri, EX.objectClass, obj.get("class"))
        add_literal(g, object_uri, EX.belongsToRegion, obj.get("region_id"))

        g.add((image_uri, EX.hasVisualObject, object_uri))

    # Атрибуты объектов
    attributes = image_data.get("Атрибуты объектов", {}).get("attributes", [])

    for i, attr in enumerate(attributes, start=1):
        attr_uri = EX[f"{safe_id(ad_id)}_visual_attribute_{i}"]

        g.add((attr_uri, RDF.type, EX.VisualAttribute))
        add_literal(g, attr_uri, EX.attributeObjectId, attr.get("object_id"))
        add_literal(g, attr_uri, EX.attributeName, attr.get("attribute"))
        add_literal(g, attr_uri, EX.attributeValue, attr.get("value"))

        g.add((image_uri, EX.hasVisualAttribute, attr_uri))

    # Цветовая разметка
    color_data = image_data.get("Цветовая разметка", {})

    add_literal(g, image_uri, EX.contrast, color_data.get("contrast"))
    add_literal(g, image_uri, EX.brightness, color_data.get("brightness"))
    add_literal(g, image_uri, EX.saturation, color_data.get("saturation"))
    add_literal(g, image_uri, EX.comment, color_data.get("comment"))

    colors = color_data.get("dominant_colors", [])

    for i, color in enumerate(colors, start=1):
        color_uri = EX[f"{safe_id(ad_id)}_color_{i}"]

        g.add((color_uri, RDF.type, EX.ColorFeature))
        add_literal(g, color_uri, EX.colorName, color.get("color"))
        add_literal(g, color_uri, EX.colorIntensity, color.get("intensity"))
        add_literal(g, color_uri, EX.colorRole, color.get("role"))

        g.add((image_uri, EX.hasColorFeature, color_uri))

    # Композиция
    composition = image_data.get("Композиция", {})

    add_literal(g, image_uri, EX.layout, composition.get("layout"))
    add_literal(g, image_uri, EX.focusArea, composition.get("focus_area"))
    add_literal(g, image_uri, EX.comment, composition.get("comment"))

    spatial_relations = composition.get("spatial_relations", [])

    for i, rel in enumerate(spatial_relations, start=1):
        rel_uri = EX[f"{safe_id(ad_id)}_spatial_relation_{i}"]

        g.add((rel_uri, RDF.type, EX.Dependency))
        add_literal(g, rel_uri, EX.relationFrom, rel.get("from"))
        add_literal(g, rel_uri, EX.relationType, rel.get("relation"))
        add_literal(g, rel_uri, EX.relationTo, rel.get("to"))

        g.add((image_uri, EX.hasSpatialRelation, rel_uri))

    # OCR
    ocr_items = image_data.get("OCR", {}).get("detected_text", [])

    for i, item in enumerate(ocr_items, start=1):
        ocr_uri = EX[f"{safe_id(ad_id)}_ocr_{i}"]

        g.add((ocr_uri, RDF.type, EX.OCRText))
        add_literal(g, ocr_uri, EX.ocrText, item.get("text"))
        add_literal(g, ocr_uri, EX.belongsToRegion, item.get("region_id"))
        add_literal(g, ocr_uri, EX.ocrConfidence, item.get("confidence"), XSD.float)

        g.add((image_uri, EX.hasOCRText, ocr_uri))

    # Семантика сцены
    semantics = image_data.get("Семантика сцены", {})

    add_literal(g, image_uri, EX.sceneType, semantics.get("scene_type"))
    add_literal(g, image_uri, EX.domain, semantics.get("domain"))
    add_literal(g, image_uri, EX.message, semantics.get("message"))
    add_literal(g, image_uri, EX.comment, semantics.get("comment"))

    # Визуальные признаки
    visual_features = image_data.get("Визуальные признаки", {})

    for category in ["signals", "risk_markers", "trust_markers"]:
        signals = visual_features.get(category, [])

        for i, signal_text in enumerate(signals, start=1):
            signal_uri = EX[f"{safe_id(ad_id)}_image_{safe_id(category)}_{i}"]

            g.add((signal_uri, RDF.type, EX.Signal))
            g.add((signal_uri, EX.signalText, Literal(signal_text)))
            g.add((signal_uri, EX.signalCategory, Literal(category)))

            g.add((image_uri, EX.hasSignal, signal_uri))

    # Сентимент изображения
    sentiment = image_data.get("Сентимент", {})

    sentiment_uri = EX[f"{safe_id(ad_id)}_image_sentiment"]

    g.add((sentiment_uri, RDF.type, EX.Sentiment))
    add_literal(g, sentiment_uri, EX.sentimentScore, sentiment.get("score"), XSD.float)
    add_literal(g, sentiment_uri, EX.sentimentLabel, sentiment.get("label"))
    add_literal(g, sentiment_uri, EX.comment, sentiment.get("comment"))

    g.add((image_uri, EX.hasSentiment, sentiment_uri))


# 6. Построение всего графа


def build_graph(data: dict) -> Graph:
    """
    Строит RDF-граф из JSON-разметки.
    """

    g = Graph()

    g.bind("ex", EX)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    add_ontology(g)

    dataset_name = data.get("dataset_name", "fraud_ads_dataset")
    dataset_uri = EX[safe_id(dataset_name)]

    g.add((dataset_uri, RDF.type, EX.Dataset))
    add_literal(g, dataset_uri, RDFS.label, dataset_name)

    ads = data.get("ads", [])

    for index, ad_data in enumerate(ads, start=1):
        ad_id = ad_data.get("ad_id", f"ad_{index}")
        ad_uri = EX[safe_id(ad_id)]

        g.add((ad_uri, RDF.type, EX.Advertisement))
        g.add((dataset_uri, EX.hasAd, ad_uri))

        add_literal(g, ad_uri, EX.hasTitle, ad_data.get("title"))
        add_literal(g, ad_uri, EX.hasLabel, ad_data.get("label"))

        modalities = ad_data.get("modalities", {})

        text_data = modalities.get("text", {})
        image_data = modalities.get("image", {})

        add_text_annotation(g, ad_uri, ad_id, text_data)
        add_image_annotation(g, ad_uri, ad_id, image_data)

    return g


# 7. SPARQL-запросы


def run_query(g: Graph, title: str, query: str) -> str:
    """
    Выполняет SPARQL-запрос и возвращает результат в виде строки.
    """

    result_lines = []
    result_lines.append(f"\n--- {title} ---")

    rows = list(g.query(query))

    if not rows:
        result_lines.append("Нет результатов")
        return "\n".join(result_lines)

    for row in rows:
        row_values = [str(value) for value in row]
        result_lines.append(" | ".join(row_values))

    return "\n".join(result_lines)


def run_sparql_examples(g: Graph) -> str:
    """
    Набор примеров SPARQL-запросов к графу знаний.
    """

    queries = [
        (
            "1. Все объявления и их метки",
            """
            PREFIX ex: <http://example.org/fraud-ads/>

            SELECT ?ad ?title ?label
            WHERE {
                ?ad a ex:Advertisement .
                OPTIONAL { ?ad ex:hasTitle ?title . }
                OPTIONAL { ?ad ex:hasLabel ?label . }
            }
            ORDER BY ?ad
            """
        ),

        (
            "2. Объявления с высоким текстовым сентиментом",
            """
            PREFIX ex: <http://example.org/fraud-ads/>

            SELECT ?ad ?title ?score
            WHERE {
                ?ad a ex:Advertisement .
                ?ad ex:hasTitle ?title .
                ?ad ex:hasTextAnnotation ?textAnn .
                ?textAnn ex:hasSentiment ?sentiment .
                ?sentiment ex:sentimentScore ?score .

                FILTER(?score >= 0.9)
            }
            ORDER BY DESC(?score)
            """
        ),

        (
            "3. Объявления, где в тексте есть MONEY или MONEY_RANGE",
            """
            PREFIX ex: <http://example.org/fraud-ads/>

            SELECT DISTINCT ?ad ?title ?entity ?type
            WHERE {
                ?ad a ex:Advertisement .
                ?ad ex:hasTitle ?title .
                ?ad ex:hasTextAnnotation ?textAnn .
                ?textAnn ex:hasNamedEntity ?entityNode .
                ?entityNode ex:entityText ?entity .
                ?entityNode ex:entityType ?type .

                FILTER(?type IN ("MONEY", "MONEY_RANGE"))
            }
            ORDER BY ?ad
            """
        ),

        (
            "4. Визуальные risk_markers по каждому объявлению",
            """
            PREFIX ex: <http://example.org/fraud-ads/>

            SELECT ?ad ?title ?signal
            WHERE {
                ?ad a ex:Advertisement .
                ?ad ex:hasTitle ?title .
                ?ad ex:hasImageAnnotation ?imageAnn .
                ?imageAnn ex:hasSignal ?signalNode .
                ?signalNode ex:signalCategory "risk_markers" .
                ?signalNode ex:signalText ?signal .
            }
            ORDER BY ?ad
            """
        ),

        (
            "5. Объявления, где OCR содержит слова про доход / выплаты / заработок",
            """
            PREFIX ex: <http://example.org/fraud-ads/>

            SELECT DISTINCT ?ad ?title ?ocr
            WHERE {
                ?ad a ex:Advertisement .
                ?ad ex:hasTitle ?title .
                ?ad ex:hasImageAnnotation ?imageAnn .
                ?imageAnn ex:hasOCRText ?ocrNode .
                ?ocrNode ex:ocrText ?ocr .

                FILTER(
                    CONTAINS(LCASE(STR(?ocr)), "доход") ||
                    CONTAINS(LCASE(STR(?ocr)), "выплат") ||
                    CONTAINS(LCASE(STR(?ocr)), "заработ")
                )
            }
            ORDER BY ?ad
            """
        ),

        (
            "6. Объявления с красным или бордовым цветом высокой интенсивности",
            """
            PREFIX ex: <http://example.org/fraud-ads/>

            SELECT DISTINCT ?ad ?title ?color ?role
            WHERE {
                ?ad a ex:Advertisement .
                ?ad ex:hasTitle ?title .
                ?ad ex:hasImageAnnotation ?imageAnn .
                ?imageAnn ex:hasColorFeature ?colorNode .
                ?colorNode ex:colorName ?color .
                ?colorNode ex:colorIntensity "high" .
                ?colorNode ex:colorRole ?role .

                FILTER(
                    CONTAINS(LCASE(STR(?color)), "red") ||
                    CONTAINS(LCASE(STR(?color)), "burgundy")
                )
            }
            ORDER BY ?ad
            """
        ),

        (
            "7. Объявления, где одновременно есть деньги в тексте и risk-маркеры на изображении",
            """
            PREFIX ex: <http://example.org/fraud-ads/>

            SELECT DISTINCT ?ad ?title
            WHERE {
                ?ad a ex:Advertisement .
                ?ad ex:hasTitle ?title .

                ?ad ex:hasTextAnnotation ?textAnn .
                ?textAnn ex:hasNamedEntity ?entityNode .
                ?entityNode ex:entityType ?entityType .

                FILTER(?entityType IN ("MONEY", "MONEY_RANGE"))

                ?ad ex:hasImageAnnotation ?imageAnn .
                ?imageAnn ex:hasSignal ?signalNode .
                ?signalNode ex:signalCategory "risk_markers" .
            }
            ORDER BY ?ad
            """
        )
    ]

    output = []
    output.append(f"Всего RDF-троек: {len(g)}")

    for title, query in queries:
        output.append(run_query(g, title, query))

    return "\n".join(output)


# 8. Точка входа


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    graph = build_graph(data)

    graph.serialize(destination=TTL_PATH, format="turtle")
    graph.serialize(destination=RDF_PATH, format="xml")

    results = run_sparql_examples(graph)

    with open(SPARQL_RESULTS_PATH, "w", encoding="utf-8") as file:
        file.write(results)

    print(results)
    print()
    print(f"RDF-граф Turtle сохранен в: {TTL_PATH}")
    print(f"RDF-граф RDF/XML сохранен в: {RDF_PATH}")
    print(f"Результаты SPARQL сохранены в: {SPARQL_RESULTS_PATH}")


if __name__ == "__main__":
    main()