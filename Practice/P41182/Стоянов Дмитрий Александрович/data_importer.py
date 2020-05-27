import json
from collections import namedtuple
from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from collections import defaultdict

with open('data.json', encoding='utf-8') as json_file:
    data = json.load(json_file, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

g = Graph()
g.parse('meme_ontology.owl', format='turtle')
prefix = dict(g.namespaces())['']
ns = Namespace(prefix)

sources_by_owner = defaultdict(list)
memes_by_creator = defaultdict(list)
liked_memes_by_viewer = defaultdict(list)
reposted_memes_by_viewer = defaultdict(list)
reported_memes_by_viewer = defaultdict(list)

for source in data.sources:
    id = URIRef(ns + source.url)
    url = Literal(source.url)
    popularity = Literal(source.popularity)
    owner = URIRef(ns + source.owner.replace(' ', '_'))
    sources_by_owner[owner].append(id)

    g.add((id, RDF.type, OWL.NamedIndividual))
    g.add((id, RDF.type, ns.Source))
    g.add((id, ns.url, url))
    g.add((id, ns.popularity, popularity))

for company in data.companies:
    id = URIRef(ns + company.name)
    name = Literal(company.name)

    g.add((id, RDF.type, OWL.NamedIndividual))
    g.add((id, RDF.type, ns.Company))
    g.add((id, ns.name, name))
    if id in sources_by_owner:
        for source in sources_by_owner[id]:
            g.add((id, ns.owns, source))

for generator in data.generators:
    id = URIRef(ns + generator.url)
    url = Literal(generator.url)

    g.add((id, RDF.type, OWL.NamedIndividual))
    g.add((id, RDF.type, ns.Generator))
    g.add((id, ns.url, url))


def add_meme(id, meme, memeType):
    url = Literal(meme.url)
    created_at = Literal(meme.createdAt)
    genre = Literal(meme.genre)
    total_likes = Literal(meme.totalLikes)
    source = URIRef(ns + meme.source)

    g.add((id, RDF.type, OWL.NamedIndividual))
    g.add((id, RDF.type, memeType))
    g.add((id, ns.url, url))
    g.add((id, ns.created_at, created_at))
    g.add((id, ns.genre, genre))
    g.add((id, ns.total_likes, total_likes))

    memes_by_creator[URIRef(ns + meme.creator)].append(id)
    g.add((id, ns.posted_in, source))
    g.add((source, ns.contains, id))

    if 'total_reposts' in meme:
        g.add((id, ns.total_reposts, Literal(meme.total_reposts)))

    if hasattr(meme, 'likedBy'):
        for person in meme.likedBy:
            liked_memes_by_viewer[URIRef(ns + person)].append(id)
    if hasattr(meme, 'repostedBy'):
        for person in meme.repostedBy:
            reposted_memes_by_viewer[URIRef(ns + person)].append(id)
    if hasattr(meme, 'reportedBy'):
        for person in meme.reportedBy:
            reported_memes_by_viewer[URIRef(ns + person)].append(id)

def add_playing_meme(id, meme, memeType):
    add_meme(id, meme, memeType)
    g.add((id, ns.length, Literal(meme.length)))


for meme in data.memes.audioMemes:
    add_playing_meme(URIRef(ns + meme.url), meme, ns.AudioMeme)

for meme in data.memes.videoMemes:
    add_playing_meme(URIRef(ns + meme.url), meme, ns.VideoMeme)

for meme in data.memes.textMemes:
    id = URIRef(ns + meme.url)
    add_meme(id, meme, ns.TextMeme)
    g.add((id, ns.content, Literal(meme.content)))

for meme in data.memes.visualMemes:
    id = URIRef(ns + meme.url)
    add_meme(id, meme, ns.VisualMeme)
    g.add((id, ns.textContent, Literal(meme.textContent)))
    if hasattr(meme, 'generator'):
        g.add((id, ns.generated_by, URIRef(ns + meme.generator)))


def add_person(id, person, person_type):
    name = Literal(person.name)
    surname = Literal(person.surname)

    g.add((id, RDF.type, OWL.NamedIndividual))
    g.add((id, RDF.type, person_type))
    g.add((id, ns.name, name))
    g.add((id, ns.surname, surname))


for viewer in data.persons.viewers:
    id = URIRef(ns + viewer.name)
    add_person(id, viewer, ns.Viewer)
    for meme in liked_memes_by_viewer[id]:
        g.add((id, ns.likes, meme))
    for meme in reposted_memes_by_viewer[id]:
        g.add((id, ns.repost, meme))
    for meme in reported_memes_by_viewer[id]:
        g.add((id, ns.report, meme))

for creator in data.persons.creators:
    id = URIRef(ns + creator.name)
    company = URIRef(ns + creator.company)
    add_person(id, creator, ns.Creator)
    g.add((id, ns.works_for, company))
    g.add((company, ns.hires, id))
    for meme in memes_by_creator[id]:
        g.add((id, ns.creates, meme))



g.serialize(destination='meme_ontology_out.owl', format='turtle')
