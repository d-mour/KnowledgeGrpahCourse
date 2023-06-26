import json
from rdflib import URIRef, BNode, Literal, Namespace, Graph, RDF, XSD


# Create a Graph
g = Graph()

# Parse in an RDF file hosted on the Internet
# g.parse(f'file://{Path(__file__).parent.resolve()}/linkedmdb-latest-dump/data.nt')
# не сработало, оно напоролось на пробелы и неизвестные символы


# class, LinkedMDB compatible
Director = URIRef("http://dbpedia.org/ontology/MovieDirector")
Actor = URIRef("http://dbpedia.org/ontology/Actor")

# dbpedia does not have ontologies for movie
# composers, stolen form lmdb
Composer = URIRef("http://data.linkedmdb.org/resource/music_contributor")

Writer = URIRef("http://dbpedia.org/ontology/ScreenWriter")
Movie = URIRef("http://dbpedia.org/ontology/Film")
Name = URIRef("http://dbpedia.org/ontology/Name")
Poster = URIRef("https://schema.org/Poster")

# other stuff
Image = "https://image.tmdb.org/t/p/w500" # for api calls. for manual inspection use www.tmdb.org

# properties
directedBy = URIRef("http://data.linkedmdb.org/resource/movie/director")
musicBy = URIRef("http://data.linkedmdb.org/resource/movie/music_contributor")
screenplayBy = URIRef("http://data.linkedmdb.org/resource/movie/writer")
performanceBy = URIRef("http://data.linkedmdb.org/resource/movie/actor")
title = URIRef("http://purl.org/dc/terms/title")
image = URIRef('https://schema.org/image')
composedBy = URIRef('http://purl.org/ontology/mo/composer')
synopsys = URIRef("http://cv.iptc.org/newscodes/genre/Synopsis")
# linkers between ids and names

directed = URIRef("http://data.linkedmdb.org/resource/movie/director_name")
music = URIRef("http://data.linkedmdb.org/resource/movie/music_contributor_name")
screenplay = URIRef("http://data.linkedmdb.org/resource/movie/writer_name")
performance = URIRef("http://data.linkedmdb.org/resource/movie/performance_actor")

Soundtrack = Literal("Musical work")
genre = URIRef('https://schema.org/genre')
instrument = URIRef("http://rdaregistry.info/Elements/e/P20215")
Rock = URIRef('http://service.ddex.net/dd/DD-AVS-001/dd/ddex_Rock')
Classical = URIRef('http://service.ddex.net/dd/DD-AVS-001/dd/ddex_ClassicalMusic')
Electro = URIRef('http://service.ddex.net/dd/DD-AVS-001/dd/ddex_ElectronicMusic')

with open('tmdb/directors.json', 'r') as f1:
    d = json.load(f1)
with open('tmdb/composers.json', 'r') as f2:
    c = json.load(f2)
with open('tmdb/writers.json', 'r') as f3:
    w = json.load(f3)
with open('tmdb/actors.json', 'r') as f4:
    a = json.load(f4)


def AddMovie(id, directors, composers, actors, writers, rating, name, poster):
    movie = URIRef("https://api.themoviedb.org/3/movie/"+id)
    g.add((movie, RDF.type, Movie))
    g.add((movie, RDF.value, Literal(rating, datatype=XSD.numeric)))
    for director in directors:
        g.add((movie, directedBy, AddPerson(director, d[str(director)], "director")))
    for composer in composers:
        g.add((movie, musicBy, AddPerson(composer, c[str(composer)], "composer")))
    for writer in writers:
        g.add((movie, screenplayBy, AddPerson(writer, w[str(writer)], "writer")))
    for actor in actors:
        g.add((movie, performanceBy, AddPerson(actor, a[str(actor)], "actor")))
    g.add((movie, title, Literal(name)))
    g.add((movie, image, Literal(Image+poster, datatype=XSD.anyURI)))
    return movie


def AddPerson(id, name, type):
    id = str(id)
    property_map = {
        "director": directed,
        "composer": music,
        "writer": screenplay,
        "actor": performance,
    }

    class_map = {
        "director": Director,
        "composer": Composer,
        "writer": Writer,
        "actor": Actor,
    }
    person = URIRef("https://api.themoviedb.org/3/person/" + id)
    g.add((person, RDF.type, class_map[type]))
    g.add((person, property_map[type], Literal(name)))
    return person


with open('tmdb/films.json', 'r') as f:
    movies = json.load(f)['movies']


for movie in movies:
    url = AddMovie(str(movie['id']), movie['directors'], movie['composers'], movie['actors'], movie['writers'], movie['rating'], movie['name'], movie['poster_url'])

# Print the number of "triples" in the Graph
print(f"Graph g has {len(g)} statements.")
# Prints: Graph g has 86 statements.

# Print out the entire Graph in the RDF Turtle format
with open('data/data.rdf', "w+", encoding="utf-8") as file:
    print(g.serialize(format="turtle"), file=file)
