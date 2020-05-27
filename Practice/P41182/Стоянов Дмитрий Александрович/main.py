from rdflib import Graph, Literal, RDF, URIRef
import requests

g = Graph()
g.parse("meme_ontology_out.owl", format='turtle')

print("graph has {} statements.".format(len(g)))

rdfs = "<http://www.w3.org/2000/01/rdf-schema#>"
prefix = "<http://www.semanticweb.org/lenovolegiony520/ontologies/2020/4/meme#>"


def execute(query):
    res = g.query(f"prefix rdfs: {rdfs} prefix : {prefix} {query}")
    for row in res:
        print('> ', row[0].split('#')[1], *row[1:])
    return res


print('\n* Top 3 memes (most likes)')
execute(
    """
    SELECT ?meme ?likes
    WHERE {
        ?meme rdf:type/rdfs:subClassOf* :Meme;
        :total_likes ?likes;
    }
    ORDER BY DESC(?likes)
    LIMIT 3
        """
)


print('\n* Number of memes created by company')
execute("""
    SELECT ?company (COUNT(?meme) as ?memCount)
    WHERE {
        ?company a :Company;
        :hires/:creates ?meme;
    }
    GROUP BY ?company
    ORDER BY DESC(?memCount)
    """)


print("\n* Meme with text content contain word 'wow', web site, where meme was generated and source")
execute("""
    SELECT ?meme ?generator ?posted_in
    WHERE {
        ?meme a :VisualMeme;
        :posted_in/:url ?posted_in;
        :textContent ?content;
        :generated_by/:url ?generator;
        FILTER regex(?content, ".*wow.*", "i")
    } 
""")

print("\n* Persons, who both like and repost at least once")
execute("""
    SELECT ?person ?liked_meme
    WHERE {
        ?person a :Viewer;
        :likes/:url ?liked_meme;
        :repost/:url ?reposted_meme;
        FILTER(?liked_meme = ?reposted_meme)
    } 
    GROUP BY ?person
""")
