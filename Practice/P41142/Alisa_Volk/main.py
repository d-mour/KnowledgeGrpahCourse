import csv
import rdflib
from rdflib import *
from tabulate import tabulate

with open('file.csv', newline='',  encoding='utf-8') as csvfile:
    data = list(csv.reader(csvfile))

headers = data[0]
data.pop(0)

def light(x):
    return {
        1: "At least 4 h of direct sun",
        2: "Over 200 ft-c, not direct sun",
        3: "75 ft-c to 200 ft-c",
        4: "25 ft-c to 75 ft-c"
    }.get(x)

def temp(x):
    return {
        1: "50°F n, 65°F d",
        2: "65°F n, 75°F d",
        3: "70°F n, 85°F d"
    }.get(x)

def rh(x):
    return {
        1: "50% or higher",
        2: "25% to 49%",
        3: "5% to 24%"
    }.get(x)

def water(x):
    return {
        1: "Keep soil mix moist",
        2: "Surface of soil mix should dry",
        3: "Soil mix can become moderately dry"
    }.get(x)

def soil(x):
    return {
        1: "Flowering house plants",
        2: "Foliage plants",
        3: "Bromeliads",
        4: "Orchids",
        5: "Succulents and cacti",
        6: "Ferns",
        7: "African violets and other Gesneriads"
    }.get(x)

for line in data:
    line[2] = int(line[2][0])
    line[3] = int(line[3][0])
    line[4] = int(line[4][0])
    line[5] = int(line[5][0])
    line[6] = int(line[6][0])
    line[2] = light(line[2])
    line[3] = temp(line[3])
    line[4] = rh(line[4])
    line[5] = water(line[5])
    line[6] = soil(line[6])

##print(tabulate(data, headers=headers, tablefmt='orgtbl'))
def MyNameSpace(g):
  for ns_prefix, namespace in g.namespaces():
    if not ns_prefix:
      return namespace
  return ""

g = rdflib.Graph()

result = g.parse("D:\\10_04(bu).xml")

for subj, pred, obj in g:
    # print(subj, pred, obj)
    if (subj, pred, obj) not in g:
       raise Exception("Not in graph")

##print("graph has {} statements.".format(len(g)))

ontology = "http://www.semanticweb.org/volka/ontologies/2021/3/untitled-ontology-4#"
ns = MyNameSpace(g)
cPlant = URIRef(ontology + "plant")
pSun = URIRef(ontology + "sun")
pTemp = URIRef(ontology + "temperature")
pWater = URIRef(ontology + "water")
pSoil = URIRef(ontology + "soil")
pHumidity = URIRef(ontology + "humidity")

for plant, name, light, temp, hum, water, soil in data:
    plantIndividual = URIRef(ontology + name.replace(" ", ""))
    g.add((plantIndividual, RDF.type, cPlant))
    g.add((plantIndividual, pSun, Literal(light)))
    g.add((plantIndividual, pTemp, Literal(temp)))
    g.add((plantIndividual, pWater, Literal(water)))
    g.add((plantIndividual, pHumidity, Literal(hum)))
    g.add((plantIndividual, pSoil, Literal(soil)))

# print(g.serialize(format="turtle").decode("utf-8"))

g.serialize("data.xml", format="xml")

# sparql

x = g.query(""""
select * 
where { ?individuals rdf:type ?plant .}
""")
result = list(x)
for p, name in result:
    print(name.replace(ontology, ""))

x = g.query("""
select * 
where { ?individuals rdf:type ?plant .} 
filter (owl:topDataProperty:sun = \"Over 200 ft-c, not direct sun\") .
""")
result = list(x)
for p, name in result:
    print(name.replace(ontology, ""))

## void

import collections

distinctForPartitions = True
def generateVoID(graph):
    typeMap = collections.defaultdict(set)
    classes = collections.defaultdict(set)

    for e, c in graph.subject_objects(RDF.type):
        classes[c].add(e)
        typeMap[e].add(c)

    triples = 0
    subjects = set()
    objects = set()
    properties = set()
    classCount = collections.defaultdict(int)
    propCount = collections.defaultdict(int)

    classProps = collections.defaultdict(set)
    classObjects = collections.defaultdict(set)
    propSubjects = collections.defaultdict(set)
    propObjects = collections.defaultdict(set)

    for subj, prop, obj in graph:
        triples += 1
        subjects.add(subj)
        properties.add(prop)
        objects.add(obj)

        # class partitions
        if subj in typeMap:
            for c in typeMap[subj]:
                classCount[c] += 1
                if distinctForPartitions:
                    classObjects[c].add(obj)
                    classProps[c].add(prop)

        # property partitions
        propCount[prop] += 1
        if distinctForPartitions:
            propObjects[prop].add(obj)
            propSubjects[prop].add(subj)

    dataset = URIRef(ontology)
    resultGraph.add((dataset, RDF.type, VOID.Dataset))

    # basic stats
    resultGraph.add((dataset, VOID.triples, Literal(triples)))
    resultGraph.add((dataset, VOID.classes, Literal(len(classes))))

    resultGraph.add((dataset, VOID.distinctObjects, Literal(len(objects))))
    resultGraph.add((dataset, VOID.distinctSubjects, Literal(len(subjects))))
    resultGraph.add((dataset, VOID.properties, Literal(len(properties))))

    for i, c in enumerate(classes):
        part = URIRef(dataset + "_class%d" % i)
        resultGraph.add((dataset, VOID.classPartition, part))
        resultGraph.add((part, RDF.type, VOID.Dataset))

        resultGraph.add((part, VOID.triples, Literal(classCount[c])))
        resultGraph.add((part, VOID.classes, Literal(1)))

        resultGraph.add((part, VOID["class"], c))

        resultGraph.add((part, VOID.entities, Literal(len(classes[c]))))
        resultGraph.add((part, VOID.distinctSubjects, Literal(len(classes[c]))))

        if distinctForPartitions:
            resultGraph.add((part, VOID.properties, Literal(len(classProps[c]))))
            resultGraph.add((part, VOID.distinctObjects, Literal(len(classObjects[c]))))

    for i, p in enumerate(properties):
        part = URIRef(dataset + "_property%d" % i)
        resultGraph.add((dataset, VOID.propertyPartition, part))
        resultGraph.add((part, RDF.type, VOID.Dataset))

        resultGraph.add((part, VOID.triples, Literal(propCount[p])))
        resultGraph.add((part, VOID.properties, Literal(1)))

        resultGraph.add((part, VOID.property, p))

        if distinctForPartitions:
            entities = 0
            propClasses = set()

            for s in propSubjects[p]:
                if s in typeMap:
                    entities += 1
                for c in typeMap[s]:
                    propClasses.add(c)

            resultGraph.add((part, VOID.entities, Literal(entities)))
            resultGraph.add((part, VOID.classes, Literal(len(propClasses))))

            resultGraph.add((part, VOID.distinctSubjects, Literal(len(propSubjects[p]))))
            resultGraph.add((part, VOID.distinctObjects, Literal(len(propObjects[p]))))

resultGraph = Graph()
graph = Graph()
graph.parse("data.xml", format="xml")
prefix = dict(graph.namespaces())['']

graph.add((prefix, DCTERMS.title, Literal("Homeplants")))
graph.add((prefix, DCTERMS.publisher, Literal('Alisa Volk', datatype=FOAF.Person)))
graph.add((prefix, DCTERMS.publisher, Literal('volk.alisa.v@ya.ru', datatype=FOAF.mbox)))
graph.add((prefix, DCTERMS.issued, Literal('2021-05-24', datatype=XSD.data)))
graph.add((prefix, VOID.distinctObjects, Literal(int(1429))))

# print(graph.serialize(format='n3'))
generateVoID(graph)
resultGraph.serialize("result.owl", format="turtle")

