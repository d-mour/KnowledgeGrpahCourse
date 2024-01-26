import json
import rdflib
from rdflib import RDF, Literal, URIRef

pokemons = json.loads(open('pokemons.json').read())
types = json.loads(open('types.json').read())
moves = json.loads(open('moves.json').read())
graph = rdflib.Graph()
graph.parse('../pokemon.owl')

prefix = r'http://www.semanticweb.org/markus/ontologies/2022/9/pokemon'

class Classes:
    POKEMON           = URIRef(prefix + '#Pokemon')
    POKEMON_MOVE      = URIRef(prefix + '#PokemonMove')
    POKEMON_SPECIES   = URIRef(prefix + '#PokemonSpecies')
    POKEMON_TYPE      = URIRef(prefix + '#PokemonType')

class ObjectProperty:
    CAN_BE_LEARNED_BY         = URIRef(prefix + '#canBeLearnedBy')
    CAN_LEARN                 = URIRef(prefix + '#canLearn')
    HAS_DOUBLE_DAMAGE_FROM    = URIRef(prefix + '#hasDoubleDamageFrom')
    HAS_DOUBLE_DAMAGE_TO      = URIRef(prefix + '#hasDoubleDamageTo')
    HAS_HALF_DAMAGE_FROM      = URIRef(prefix + '#hasHalfDamageFrom')
    HAS_HALF_DAMAGE_TO        = URIRef(prefix + '#hasHalfDamageTo')
    HAS_MOVE_TYPE             = URIRef(prefix + '#hasMoveType')
    HAS_NO_DAMAGE_FROM        = URIRef(prefix + '#hasNoDamageFrom')
    HAS_NO_DAMAGE_TO          = URIRef(prefix + '#hasNoDamageTo')
    HAS_POKEMON_TYPE          = URIRef(prefix + '#hasPokemonType')
    HAS_SPECIES               = URIRef(prefix + '#hasSpecies')
    IS_TYPE_OF_MOVE            = URIRef(prefix + '#isTypeOfMove')
    IS_SPECIES_OF_POKEMON     = URIRef(prefix + '#isSpeciesOfPokemon')
    IS_TYPE_OF_POKEMON        = URIRef(prefix + '#isTypeOfPokemon')


class DataProperty:
    ATTACK          = URIRef(prefix + '#attack')
    DEFENSE         = URIRef(prefix + '#defense')
    DESCRIPTION     = URIRef(prefix + '#description')
    HEIGHT          = URIRef(prefix + '#height')
    HP              = URIRef(prefix + '#hp')
    NAME            = URIRef(prefix + '#name')
    SPEED           = URIRef(prefix + '#speed')
    WEIGHT          = URIRef(prefix + '#weight')


def create_type(type_name, class_name, suffix = ''):
    type_uri = URIRef(prefix + f'#{type_name}' + suffix)
    if (type_uri, None, None) not in graph:
      graph.add((type_uri, RDF.type, class_name))
    return type_uri


def add_damages(type_name, damages):
    type_uri = create_type(type_name, Classes.POKEMON_TYPE, '-type')

    damage_relations = damages['damage_relations']

    double_damage_from = damage_relations['double_damage_from']
    double_damage_to = damage_relations['double_damage_to']

    half_damage_from = damage_relations['half_damage_from']
    half_damage_to = damage_relations['half_damage_to']

    no_damage_from = damage_relations['no_damage_from']
    no_damage_to = damage_relations['no_damage_to']


    for p_type_from in double_damage_from:
        triple = (type_uri, ObjectProperty.HAS_DOUBLE_DAMAGE_FROM, create_type(p_type_from, Classes.POKEMON_TYPE, '-type'))
        graph.add(triple)

    for p_type_to in double_damage_to:
        triple = (type_uri, ObjectProperty.HAS_DOUBLE_DAMAGE_TO, create_type(p_type_to, Classes.POKEMON_TYPE, '-type'))
        graph.add(triple)


    for p_type_from in half_damage_from:
        triple = (type_uri, ObjectProperty.HAS_HALF_DAMAGE_FROM, create_type(p_type_from, Classes.POKEMON_TYPE, '-type'))
        graph.add(triple)

    for p_type_to in half_damage_to:
        triple = (type_uri, ObjectProperty.HAS_HALF_DAMAGE_TO, create_type(p_type_to, Classes.POKEMON_TYPE, '-type'))
        graph.add(triple)


    for p_type_from in no_damage_from:
        triple = (type_uri, ObjectProperty.HAS_NO_DAMAGE_FROM, create_type(p_type_from, Classes.POKEMON_TYPE, '-type'))
        graph.add(triple)

    for p_type_to in no_damage_to:
        triple = (type_uri, ObjectProperty.HAS_NO_DAMAGE_TO, create_type(p_type_to, Classes.POKEMON_TYPE, '-type'))
        graph.add(triple)

    graph.add((type_uri, DataProperty.NAME, Literal(type_name)))
    

def add_moves(move_name, move):
        move_uri = create_type(move_name, Classes.POKEMON_MOVE, '-move')

        description = move['description']
        ptype = move['type']
        ptype_uri = create_type(ptype, Classes.POKEMON_TYPE, '-type')

        graph.add((move_uri, DataProperty.NAME, Literal(move_name)))
        graph.add((move_uri, DataProperty.DESCRIPTION, Literal(description)))

        graph.add((move_uri, ObjectProperty.HAS_MOVE_TYPE, ptype_uri))
        graph.add((ptype_uri, ObjectProperty.IS_TYPE_OF_MOVE, move_uri))


def add_pokemons_and_species(pokemon_name, pokemon):
    pokemon_uri = create_type(pokemon_name, Classes.POKEMON, '-poke')
    species_uri = create_type(pokemon['species'], Classes.POKEMON_SPECIES, '-species')

    graph.add((pokemon_uri, ObjectProperty.HAS_SPECIES, species_uri))
    graph.add((species_uri, ObjectProperty.IS_SPECIES_OF_POKEMON, pokemon_uri))

    graph.add((pokemon_uri, DataProperty.NAME, Literal(pokemon['name'])))
    graph.add((pokemon_uri, DataProperty.DESCRIPTION, Literal(pokemon['description'])))
    graph.add((pokemon_uri, DataProperty.HP, Literal(int(pokemon['hp']))))
    graph.add((pokemon_uri, DataProperty.ATTACK, Literal(int(pokemon['attack']))))
    graph.add((pokemon_uri, DataProperty.DEFENSE, Literal(int(pokemon['defense']))))
    graph.add((pokemon_uri, DataProperty.SPEED, Literal(int(pokemon['speed']))))
    graph.add((pokemon_uri, DataProperty.WEIGHT, Literal(int(pokemon['weight']))))
    graph.add((pokemon_uri, DataProperty.HEIGHT, Literal(int(pokemon['height']))))

    for ptype in pokemon['types']:
        type_uri = create_type(ptype, Classes.POKEMON_TYPE, '-type')
        graph.add((pokemon_uri, ObjectProperty.HAS_POKEMON_TYPE, type_uri))
        graph.add((type_uri, ObjectProperty.IS_TYPE_OF_POKEMON, pokemon_uri))
    for move in pokemon['moves']:
        move_uri = create_type(move, Classes.POKEMON_MOVE, '-move')
        graph.add((pokemon_uri, ObjectProperty.CAN_LEARN, move_uri))
        graph.add((move_uri, ObjectProperty.CAN_BE_LEARNED_BY, pokemon_uri))


def execute():
    for key, value in types.items():
        add_damages(key, value)
    for key, value in moves.items():
        add_moves(key, value)
    for key, value in pokemons.items():
        if 'hp' not in value.keys():
            continue
        add_pokemons_and_species(key, value)

    graph.serialize(destination='../pokemons_cut.owl', format='json-ld')

execute()