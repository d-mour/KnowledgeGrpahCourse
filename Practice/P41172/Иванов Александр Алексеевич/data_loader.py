import json
from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

with open('data.json', encoding='utf-8') as json_file:
    data = json.load(json_file)
ns = Namespace('http://www.semanticweb.org/alivanov/ontologies/2020/5/untitled-ontology-3#')
g = Graph()
g.parse("bands_ontology.owl", format='turtle')


def convert_to_uri(name):
    name = name.replace(" ", "_")
    for char in ['®', '#', ',', '`']:
        name = name.replace(char, '')
    return name


def import_albums(data):
    print("Import albums")
    for album in data:
        name = ns + URIRef(convert_to_uri(album["name"]))
        year = Literal(album['year'])
        genre = album['genre']
        artist = album['artist']
        g.add((name, RDF.type, ns.Album))
        g.add((name, RDF.type, OWL.NamedIndividual))
        g.add((name, ns.wasProduced, URIRef(ns + convert_to_uri(artist))))
        g.add((name, ns.year, year))
        g.add((name, ns.hasGenreOf, URIRef(ns + convert_to_uri(genre))))


def import_artists(data):
    print("Import artists")
    for artist in data:
        name = ns + URIRef(convert_to_uri(artist["name"]))
        formed = Literal(artist['formed'])
        genre = artist['genre']
        albums = artist['albums']
        g.add((name, RDF.type, ns.Artist))
        g.add((name, RDF.type, OWL.NamedIndividual))
        g.add((name, ns.formed, formed))
        g.add((name, ns.hasGenreOf, URIRef(ns + convert_to_uri(genre))))
        for a in albums:
            a_name = ns + URIRef(convert_to_uri(a))
            g.add((name, ns.hasAlbum, a_name))
            if (a_name, RDF.type, ns.Album) not in g:
                g.add((a_name, RDF.type, ns.Album))
                g.add((a_name, RDF.type, OWL.NamedIndividual))
                g.add((a_name, ns.wasProduced, URIRef(ns + convert_to_uri(name))))
                g.add((a_name, ns.hasGenreOf, URIRef(ns + convert_to_uri(genre))))


def import_concerts(data):
    print("Import concerts")
    for concert in data:
        place = Literal(concert["place"])
        date = Literal(concert["date"])
        performer = convert_to_uri(concert["performer"])
        name = ns + URIRef(performer + "_in_" + convert_to_uri(place))
        g.add((name, RDF.type, ns.Concert))
        g.add((name, RDF.type, OWL.NamedIndividual))
        g.add((name, ns.place, place))
        g.add((name, ns.date, date))
        g.add((name, ns.performer, URIRef(ns + performer)))


def import_tracks(data):
    print("Import tracks")
    for track in data:
        name = ns + URIRef(convert_to_uri(track["name"]))
        album = track['album']
        g.add((name, RDF.type, ns.Track))
        g.add((name, RDF.type, OWL.NamedIndividual))
        g.add((name, ns.fromAlbum, URIRef(ns + convert_to_uri(album))))


imports = {
    "Albums": import_albums,
    "Artists": import_artists,
    "Concerts": import_concerts,
    "Tracks": import_tracks,
}

for key in data.keys():
    imports[key](data[key])

# print(g.serialize(format="turtle").decode("utf-8"))
g.serialize(destination='bands_ontology_res.owl', format='turtle')