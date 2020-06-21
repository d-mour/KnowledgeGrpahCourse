import rdflib

PREFIXES = """
prefix : <http://www.semanticweb.org/ff220v/ontologies/my_first_ontology#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
"""

g = rdflib.Graph()

with open("computer_hardware_ontology.owl", "r") as f:
    g.parse(source=f)
print(f"Graph has {len(g)} statements.")
print(g.serialize(format="turtle").decode("utf-8"))


cases = """
SELECT ?x
WHERE { 
    ?x rdfs:subClassOf :Case 
}     
"""

computers = """
SELECT ?x
WHERE { 
    ?x rdf:type owl:NamedIndividual
}     
"""

computers_with_intel = """
SELECT ?x
WHERE { 
    ?x rdfs:subClassOf :Computer .
    ?x rdfs:subClassOf [owl:onProperty :includes ;
                        owl:someValuesFrom :someIntelCPU ]
}     
"""


computers_with_amd_cooler = """
SELECT ?x
WHERE { 
    ?x rdfs:subClassOf :Computer .
    ?x rdfs:subClassOf [owl:onProperty :includes ;
                        owl:someValuesFrom :someAMDCooler ]
}     
"""


gaming_computer_individuals = """
SELECT ?x
WHERE { 
    ?x rdf:type owl:NamedIndividual .
    ?x a :someOfficeComputer
}     
"""


def make_a_query(query, name=None):
    res = g.query(f"{PREFIXES}\n{query}")
    print(name if name else "")
    for row in res:
        print(row)


make_a_query(cases, "cases")
make_a_query(computers, "computers")
make_a_query(computers_with_intel, "computers_with_intel")
make_a_query(computers_with_amd_cooler, "computers_with_amd_cooler")
make_a_query(gaming_computer_individuals, "gaming_computer_individuals")

