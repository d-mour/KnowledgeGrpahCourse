from rdflib import Graph


count_related_creations_for_drivers = """
    SELECT ?driverName ?driverSurname (count(?relatedCreation) AS ?creationsCount)
    WHERE {
        ?driver a f1:Driver ;
                f1:firstName ?driverName ;
                f1:lastName ?driverSurname .
        ?relatedCreation rdf:type/rdfs:subClassOf* f1:RelatedCreation ;
                          f1:isAbout ?driver .
    }
    GROUP BY ?driver
    ORDER BY desc(?creationsCount)
    LIMIT 10
    OFFSET 1
"""

count_team_wins_and_movies = """
    SELECT ?teamName (count(?result) AS ?winsCount) (count(?movie) AS ?moviesCount)
    WHERE {
        ?team a f1:Team ;
              f1:teamName ?teamName .
        { 
        ?result a f1:ConstructorStanding ;
                  f1:seasonConstructorResultIsRelatedTo ?team ;
                  f1:totalPosition ?pos .
        FILTER (?pos = 1)
        }
        UNION
        { 
        ?movie a f1:Movie ;
               f1:isAbout ?team .
        }
    }
    GROUP BY ?team
    ORDER BY desc(?winsCount)
"""

number_of_creation_about_died = """
    SELECT (count(distinct ?relatedCreation) AS ?creationsCount)
    WHERE {
        ?accident a f1:DeathAccident .
        ?driver a f1:Driver .
        FILTER EXISTS {
            ?driver f1:hasDiedIn ?accident .
        }
        ?relatedCreation rdf:type/rdfs:subClassOf* f1:RelatedCreation ;
                          f1:isAbout ?driver .
    }
"""

most_popular_cars_data_request = """
    SELECT ?carModel ?carSpecifications ?carEngine ?carDimensions (count(?creation) AS ?creationsCount)
    WHERE {
        ?car a f1:Car ;
             f1:carModel ?carModel .
        OPTIONAL {
            ?car f1:specifications ?carSpecifications .
        }
        OPTIONAL {
            ?car f1:engineDescription ?carEngine .
        }
        OPTIONAL {
            ?car f1:dimensions ?carDimensions .
        }
        ?creation rdf:type/rdfs:subClassOf* f1:RelatedCreation ;
                          f1:isAbout ?car .
    }
    GROUP BY ?car
    ORDER BY desc(?creationsCount)
    OFFSET 1
"""

avg_laps_in_books_with_rating = """
    SELECT (avg(?laps) AS ?lapsAverage)
    WHERE {
        ?grandPrix a f1:GrandPrix ;
                   f1:totalLaps ?laps .
        ?book a f1:Book ;
              f1:goodreadsRating ?rating ;
              f1:isAbout ?grandPrix .
        FILTER (?rating >= 4.00)
    }
"""


def run_queries(graph_path, data_format):
    f1_graph = Graph().parse(graph_path, format=data_format)
    for row in f1_graph.query(count_related_creations_for_drivers):
        print(f'Driver {row.driverName} {row.driverSurname}: {row.creationsCount} related creations')
    for row in f1_graph.query(count_team_wins_and_movies):
        print(f'Team {row.teamName} won {row.winsCount} seasons, has {row.moviesCount} movies')
    for row in f1_graph.query(number_of_creation_about_died):
        print(f'Number of creations about drivers died in accidents is: {row.creationsCount} ')
    for row in f1_graph.query(most_popular_cars_data_request):
        print(f'{row.carModel} ({row.creationsCount} books and movies):\n{row.carSpecifications}\n{row.carEngine}\n'
              f'{row.carDimensions}')
    for row in f1_graph.query(avg_laps_in_books_with_rating):
        print(f'Average number of laps in grand prix described in books with rating >= 4.00: {row.lapsAverage} ')
