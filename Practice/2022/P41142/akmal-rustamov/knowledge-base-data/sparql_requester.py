from rdflib import Graph

# Характеристики вин произведённых в указанном регионе
QUERY_1 = """
    SELECT DISTINCT ?wine ?grape ?flavor ?color ?sugar
	    WHERE {
		    ?wine a/rdfs:subClassOf* wine:wine ;
		    wine:locatedIn wine:NapaRegion .

		    OPTIONAL {
			    ?grape a wine:WineGrape ;
			    wine:madeIntoWine ?wine .
		    }

		    OPTIONAL {
			    ?wine wine:hasFlavor ?flavor .
		    }

		    OPTIONAL {
			    ?wine wine:hasColor ?color .
		    }

		    OPTIONAL {
			    ?wine wine:hasSugar ?sugar .
		    }
	    }
"""

# Характеристики вин собранных из урожая указанного года в указанном регионе
QUERY_2 = """
    SELECT DISTINCT ?wine ?grape ?flavor ?color ?sugar
	    WHERE {
		    ?wine a/rdfs:subClassOf* wine:wine ;
		    wine:locatedIn wine:NapaRegion .

		    ?wine wine:hasVintageYear ?year .
		    ?year wine:yearValue ?value .
		    FILTER (?value = "1998"^^xsd:positiveInteger) .

		    OPTIONAL {
			    ?grape a wine:WineGrape ;
			    wine:madeIntoWine ?wine .
		    }

		    OPTIONAL {
			    ?wine wine:hasFlavor ?flavor .
		    }

		    OPTIONAL {
			    ?wine wine:hasColor ?color .
		    }

		    OPTIONAL {
			    ?wine wine:hasSugar ?sugar .
		    }
	    }
"""

# Список полусладких вин произведённых из указанного вида винограда
QUERY_3 = """
    SELECT DISTINCT ?wine
	    WHERE {
		    ?wine a/rdfs:subClassOf* ?type ;
		    wine:hasSugar wine:OffDry ;
		    wine:madeFromGrape wine:CheninBlancGrape .
	    }
"""

# Список красных вин произведённых указаной винодельней
QUERY_4 = """
    SELECT DISTINCT ?wine
	    WHERE {
		    ?wine a/rdfs:subClassOf* ?type ;
		    wine:hasColor wine:Red  .
		
		    ?winery a wine:Winery ;
		    wine:producesWine ?wine .
	    }
"""


def run_queries(graph_path, data_format):
    graph = Graph().parse(graph_path, format=data_format)

    for row in graph.query(QUERY_1):
        print(f'{row.wine}: {row.grape} {row.flavor} {row.color} {row.sugar}')

    for row in graph.query(QUERY_2):
        print(f'{row.wine}: {row.grape} {row.flavor} {row.color} {row.sugar}')

    for row in graph.query(QUERY_3):
        print(f'{row.wine}')

    for row in graph.query(QUERY_4):
        print(f'{row.wine}')
