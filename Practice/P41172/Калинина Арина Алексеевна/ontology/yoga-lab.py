from rdflib import ConjunctiveGraph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib.plugins.sparql import prepareQuery

def printElements(rdfGraph):
    individuals = rdfGraph.subjects(RDF.type, asana)
    for individual in individuals:
        print(rdfGraph.label(individual))

rdfGraph = ConjunctiveGraph()
try:
    rdfGraph.parse("yoga-ontology.rdf", format="xml")
except:
    print("Error")

ns = Namespace('http://webprotege.stanford.edu/')
asana = ns.RD1UGDkMwbwNp3Nh9Gy5W3M         # root element of classification
sukhasana = ns.R8SV4CeNnDntt7K2HTjws64     # element to delete
description = ns.R7zDsGb0eQYf6uJETHG3qBx   # predicate for dataprop (description)
newAsana = ns.newElement1

positiveAffect = rdfGraph.subjects(RDFS.label, Literal("положительно влияет на", "ru")).__next__()
negativeAffect = rdfGraph.subjects(RDFS.label, Literal("отрицательно влияет на", "ru")).__next__()
backbone = rdfGraph.subjects(RDFS.label, Literal("Позвоночник", lang="ru")).__next__()

print(f"\nLabel of root element is {rdfGraph.label(asana)}")

print("\nFull information of root element:")
for po in rdfGraph.predicate_objects(asana):
    print(po)

print("\nGetting all instances for type of root element")
printElements(rdfGraph)

#Adding new asana
bnode = BNode()             # class relations
rdfGraph.add((newAsana, RDF.type, asana))
rdfGraph.add((newAsana, RDF.type, bnode))
rdfGraph.add((newAsana, RDFS.label, Literal("Новая асана", lang="ru")))
rdfGraph.add((newAsana, description, Literal("Описание процесса выполнения", datatype=XSD.string)))
rdfGraph.add((bnode, OWL.onProperty, URIRef(negativeAffect)))
rdfGraph.add((bnode, OWL.someValuesOf, URIRef(backbone)))

print("\nGetting with new element")
printElements(rdfGraph)

#Remove sukhasana
rdfGraph.remove((sukhasana, None, None))

print("\nGetting with deleted element")
printElements(rdfGraph)

#Search for all categories which affects 'позвоночник'
ds = URIRef(description).n3(rdfGraph.namespace_manager)         # convert to NS:suffix format
print(f"{description} -> {ds}")

pq = prepareQuery(f"""SELECT ?asana ?label ?description WHERE {{
  ?asana rdf:type ?o .
  ?asana {ds} ?description .
  ?asana rdfs:label ?label .
  ?o owl:onProperty ?affect .
  ?o owl:someValuesFrom ?affectTo .
}}""", initNs={"webprotege":ns, "owl": OWL})

q = rdfGraph.query(pq, initBindings={
    "affect": URIRef(positiveAffect),
    "affectTo": URIRef(backbone)
})
for result in q:
    print(result)
