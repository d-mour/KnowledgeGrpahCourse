from rdflib import Graph, Namespace, RDF, Literal, URIRef

from data_handler import Pair


def update_ontology_graph(coffe_types: dict[str, list[Pair[str, str]]]):
    g = Graph()
    g.parse("coffe.rdf", format="xml")
    EX = Namespace("http://www.semanticweb.org/alinaarmut/ontologies/2024/9/untitled-ontology-29#")
    g.bind("ex", EX)
    rm = ["«", "»"," ",",", ".", '"']
    for name, ingredients in coffe_types.items():
        for i in rm:
            name.replace(i, "")
        drink_uri = EX[name.replace(" ", "_")]
        g.add((drink_uri, RDF.type, EX.Напиток))

        #for ingredient in ingredients:
        #    ingredient_property = URIRef(EX + ingredient.name.replace(" ", "_").replace(",", "").replace('"', ""))
        #    g.add((drink_uri, ingredient_property, Literal(ingredient.count)))

    g.serialize("coffee.rdf", formate="xml")

