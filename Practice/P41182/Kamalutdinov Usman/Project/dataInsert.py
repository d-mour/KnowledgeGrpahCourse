import json
from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL


with open('datatoinsert.json', encoding='utf-8') as json_file:
    data = json.load(json_file)

namespace = Namespace('http://www.semanticweb.org/fairytail/ontologies/2020/4/')

graph = Graph()
graph.parse("333.owl", format='turtle')

"""
This method inserts data to ontology by parsing json file. 
"""
def insert_data(data, category):
    if category == 'Model':
        for key in data[category].keys():
            if key == 'Ceed':
                cls = namespace.Ceed
            elif key == 'Ceed_SW':
                cls = namespace.Ceed_SW
            elif key == 'Cerato':
                cls = namespace.Cerato
            elif key == 'Cerato_Classic':
                cls = namespace.Cerato_Classic
            elif key == 'K900':
                cls = namespace.K900
            elif key == 'Mohave':
                cls = namespace.Mohave
            elif key == 'Optima':
                cls = namespace.Optima
            elif key == 'Picanto':
                cls = namespace.Picanto
            elif key == 'ProCeed':
                cls = namespace.ProCeed
            elif key == 'Rio':
                cls = namespace.Rio
            elif key == 'Seltos':
                cls = namespace.Seltos
            elif key == 'Sorento':
                cls = namespace.Sorento
            elif key == 'Sorento_Prime':
                cls = namespace.Sorento_Prime
            elif key == 'Soul':
                cls = namespace.Soul
            elif key == 'Sportage':
                cls = namespace.Sportage
            elif key == 'Stinger':
                cls = namespace.Stinger
                
            for Model in data[category][key]:
                name = Model['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = namespace + URIRef(name)
                price = Literal(Model['Price'])
                complectation = Literal(Model['Complectation'])
                drive = Literal(Model['Drive'])
                transmission = Literal(Model['Transmission'])
                type = Literal(Model['Type']).replace(' ', '_')
                power = Literal(Model['Power'])
                volume = Literal(Model['Volume'])
                year = Literal(Model['Year'])

                graph.add((name, RDF.type, OWL.NamedIndividual))
                graph.add((name, RDF.type, cls))
                graph.add((name, namespace.has_complectation, URIRef(namespace + complectation)))
                graph.add((name, namespace.has_type, URIRef(namespace + type)))
                graph.add((name, namespace.has_drive, URIRef(namespace + drive)))
                graph.add((name, namespace.has_transmission, URIRef(namespace + transmission)))
                graph.add((name, namespace.kiahas_price, price))
                graph.add((name, namespace.has_year, year))
                graph.add((name, namespace.has_engine_power, power))
                graph.add((name, namespace.has_engine_volume, volume))

#Insert data by categories
insert_data(data, 'Model')


print(graph.serialize(format="turtle").decode("utf-8"))

graph.serialize(destination='new.owl', format='turtle')
