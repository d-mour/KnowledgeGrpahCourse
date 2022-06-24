from get_data.get_data import *
from rdf.parse_owl import *
from rdf.sparql import *
from rdf.void import *
from rdflib import Graph
from pyshacl import validate
from embeddings.make_embeddings import *


def main():
    # 1
    # url = 'https://www.d20pfsrd.com/bestiary/monster-listings/aberrations/bee-man/'
    # bst = get_page(url)
    # put_page(bst)
    # print('\n')
    # 2
    # Create a Graph
    g = Graph()
    # Parse in an RDF file
    g.parse("./src/resources/graph.owl")
    lang = set()
    beasts = set()
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/aberrations'
    get_data(g, url, beasts, lang)
    print("ABERRATIONS FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/animals'
    get_data(g, url, beasts, lang)
    print("ANIMALS FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/constructs'
    get_data(g, url, beasts, lang)
    print("CONSTRUCTS FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/dragons'
    get_data(g, url, beasts, lang)
    print("DRAGONS FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/fey'
    get_data(g, url, beasts, lang)
    print("FEY FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/humanoids'
    get_data(g, url, beasts, lang)
    print("HUMANOIDS FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/magical-beasts'
    get_data(g, url, beasts, lang)
    print("MAG BEASTS FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/monstrous-humanoids'
    get_data(g, url, beasts, lang)
    print("MONSTR HUM FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/oozes'
    get_data(g, url, beasts, lang)
    print("OOZES FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/outsiders'
    get_data(g, url, beasts, lang)
    print("OUTSIDERS FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/plants'
    get_data(g, url, beasts, lang)
    print("PLANTS FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/undead'
    get_data(g, url, beasts, lang)
    print("UNDEAD FINISHED")
    url = 'https://www.d20pfsrd.com/bestiary/monster-listings/vermin'
    get_data(g, url, beasts, lang)
    print("VERMIN FINISHED")

    g.serialize(destination='./src/resources/graph_with_beasts.owl', format='turtle')
    # 3
    make_sparql_req()
    # parse_owl("./src/resources/graph_resaved.owl")
    make_void()
    # 4
    g.parse("./src/resources/graph_resaved.owl")
    print("parsed")
    r = validate(g,
                 inference='rdfs',
                 abort_on_first=False,
                 allow_infos=False,
                 allow_warnings=False,
                 meta_shacl=False,
                 advanced=False,
                 js=False,
                 debug=False)
    print(r)
    # 5
    df, triples = make_triplets()
    train, test = split_train_test(triples)
    # print(train[0])
    build_model(train, test)
    clustering(df)
    return


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

