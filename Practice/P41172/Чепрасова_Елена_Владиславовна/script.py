from rdflib import Graph, Literal, URIRef
from rdflib import RDF, RDFS, FOAF, XSD, OWL
from pprint import pprint
import json
import re

g = Graph()

g.parse('band-ontology.ttl', format='turtle')

prefix = dict(g.namespaces())['']

BAND_ON_QUEEN_TOUR_QUERY =        """
        SELECT ?band
        WHERE {{
            ?band rdf:type :Band;
                :goes_on :Queen_II_Tour;
        }}
        """
BAND_ON_QUEEN_TOUR_WITH_ALBUM_QUERY = """
            SELECT ?band
            WHERE {{
                ?band rdf:type :Band;
                    :goes_on :Queen_II_Tour;
                    :creates :A_Night_at_the_Opera;
            }}
            """

COMMON_BAND_MATES_QUERY = """
        SELECT ?m
        WHERE {{
            ?m rdf:type :Musician;
                :works_in :Queen;
                :works_in :Smile;
        }}
        """

def save_output_file():
	with open('band-ontology-out.ttl', 'wb+') as f:
		f.write(g.serialize(format='turtle'))

def label(s):
    return str(g.label(s))

def normalize(name):
    return re.sub('\W', '_', name)

def ref(name):
    return URIRef(prefix + normalize(name))

def propvalue(key, prop):
    for o, p, s in g:
        if o == key and p == prop:
            return s

def add(entries):
    for e in entries:
        g.add(e)

def build_mapping():
	return dict((o, (propvalue(o, RDFS.domain), propvalue(o, RDFS.range)))
           for o, p, s in g
           if p == RDF.type and s == OWL.ObjectProperty)


mapping = build_mapping()
# {'manages': (Manager, Band)}

with open('data.json', 'r') as f:
    json_array = json.load(f)
    #print(json_array)
    for row in json_array:
    	obj = row['Object']
    	predicate = row['predicate']
    	subject = row['subject']
    	pred = ref(predicate)
    	if pred not in mapping:
    		raise Exception('Unknown predicate: ' + predicate)
    	oc, sc = mapping[pred]
    	add([
            (ref(obj), RDF.type, OWL.NamedIndividual),
            (ref(obj), RDF.type, oc),
            (ref(obj), RDFS.label, Literal(obj)),

            (ref(subject), RDF.type, OWL.NamedIndividual),
            (ref(subject), RDF.type, sc),
            (ref(subject), RDFS.label, Literal(subject)),

            (ref(obj), pred, ref(subject))
        ])

def execute(query):
    res = g.query(f"PREFIX : <{prefix}> " + query)
    if len(res.vars) == 1:
        return list(map(lambda x: x[res.vars[0]], res))
    else:
        return list(res)

bands_on_queen_tour = execute(BAND_ON_QUEEN_TOUR_QUERY)
print('Bands on queen tour: ', bands_on_queen_tour, '\n')


queen = execute(BAND_ON_QUEEN_TOUR_WITH_ALBUM_QUERY)

print('Band on Queen tour that created Night at the Opera album: ', queen, '\n')

common_band_mates = execute(COMMON_BAND_MATES_QUERY)
print('Musicians working in Queen and Smile: ', common_band_mates, '\n')

save_output_file()