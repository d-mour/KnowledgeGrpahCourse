import sys
import getopt
import uuid

from rdflib import Graph, URIRef, RDF, Literal
from rdflib.plugins.sparql import prepareQuery
from utils.input_helper import get_option, get_string
from tabulate import tabulate

MENU_PROMPT = """Menu:
1. Get all variables for server
2. Get all values of variable
3. Add variable
4. Save to file
5. Exit"""

VARS_NS = URIRef('http://www.semanticweb.org/variables-ontology#')
VAR_FORMAT = 'http://www.semanticweb.org/variables-ontology#{name}-{suffix}'
TYPE_FORMAT = 'http://www.semanticweb.org/variables-ontology#{name}'


# variable properties
VAR_NAME = URIRef('http://www.semanticweb.org/variables-ontology#hasName')
VAR_VALUE = URIRef('http://www.semanticweb.org/variables-ontology#hasValue')
VAR_SERV_TYPE = URIRef('http://www.semanticweb.org/variables-ontology#hasServiceType')
VAR_LOCATION = URIRef('http://www.semanticweb.org/variables-ontology#hasLocation')


# dynamic values of properties
class PreloadValues:
    service_types = []
    regions = []
    clouds = []
    zones = []
    vars_classes = []


def save_file(graph, filename):
    print(f'Save ontology to {filename}')
    with open(filename, 'w') as file:
        file.write(graph.serialize(format='xml').decode('utf-8'))


def print_table(table, headers):
    string_table = []
    for row in table:
        row_string = []
        for entity in row:
            if isinstance(entity, Literal):
                row_string.append(entity._value)
            elif isinstance(entity, URIRef):
                row_string.append(entity.toPython())
            else:
                row_string.append(entity)
        string_table.append(row_string)
    print(tabulate(string_table, headers=headers, tablefmt='orgtbl'))


def get_variables_for_server(graph):
    try:
        zone = get_option('Select zone', PreloadValues.zones)
        service_type = get_option('Select service_type', PreloadValues.service_types)
        region = get_option('Select region', PreloadValues.regions)
        cloud = get_option('Select cloud', PreloadValues.clouds)
    except Exception as ex:
        print(repr(ex))
        return

    query_string = f"""SELECT ?name ?value ?variable ?zone ?serviceType ?region ?cloud 
                WHERE {{ ?class	rdfs:subClassOf*	vars:Variable.
                        ?variable 	rdf:type		?class;
                        vars:hasName	?name;
                        vars:hasValue	?value .

                    OPTIONAL{{  ?variable vars:hasServiceType   ?serviceType}}
                    FILTER(!bound(?serviceType) || ?serviceType = vars:{service_type})

                    OPTIONAL{{	?variable	vars:hasLocation 	?zone.
                                ?zone 	    rdf:type 		    vars:Zone.}}
                    FILTER(!bound(?zone) || ?zone = vars:{zone})

                    
                    OPTIONAL{{	?variable	vars:hasLocation 	?region.
                                ?region	    rdf:type 		    vars:Region.}}
                    FILTER(!bound(?region) || ?region = vars:{region})
                    
                    OPTIONAL{{	?variable	vars:hasLocation 	?cloud.
                                ?cloud	    rdf:type 		    vars:Cloud.}}
                    FILTER(!bound(?cloud) || ?cloud = vars:{cloud})
                }}
                GROUP BY ?name
"""
    print(query_string)
    result = graph.query(
        prepareQuery(
            query_string,
            initNs={
                'vars': VARS_NS
            }
        )
    )
    print_table(result, ['Name', 'Value', 'Instance', 'Zone', 'Service Type', 'Region', 'Cloud'])


def get_all_variable_values(graph):
    try:
        variable_name = get_string('Variable name')
    except Exception as ex:
        print(repr(ex))
        return

    query_string = f"""SELECT ?name ?value ?variable ?zone ?serviceType ?region ?cloud 
                    WHERE {{ ?class	rdfs:subClassOf*	vars:Variable.
                            ?variable 	rdf:type		?class;
                            vars:hasName	?name;
                            vars:hasValue	?value .
                        OPTIONAL{{	?variable	vars:hasLocation 	?zone.
                                    ?zone 	    rdf:type 		    vars:Zone.}}

                        OPTIONAL{{  ?variable vars:hasServiceType   ?serviceType}}

                        OPTIONAL{{	?variable	vars:hasLocation 	?region.
                                    ?region	    rdf:type 		    vars:Region.}}

                        OPTIONAL{{	?variable	vars:hasLocation 	?cloud.
                                    ?cloud	    rdf:type 		    vars:Cloud.}}
                        FILTER(?name = "{variable_name}")
                    }}"""
    print(query_string)
    result = graph.query(
        prepareQuery(
            query_string,
            initNs={
                'vars': VARS_NS
            }
        )
    )
    print_table(result, ['Name', 'Value', 'Instance', 'Zone', 'Service Type', 'Region', 'Cloud'])


def _select_str_values_by_type(graph, type):
    result = []
    for row in graph.query(prepareQuery(f'SELECT ?value WHERE {{?value rdf:type vars:{type}}}',
                                        initNs={'vars': VARS_NS})):
        result.append(row[0].toPython().split('#')[1])
    return result


def _select_subclasses(graph, type):
    result = []
    for row in graph.query(prepareQuery(f'SELECT ?value WHERE {{?value rdfs:subClassOf* vars:{type}}}',
                                        initNs={'vars': VARS_NS})):
        result.append(row[0])
    return result


def add_variable(graph):
    try:
        name = get_string('Variable name')
        value = get_string('Variable value')
        type = get_option('Select type (required)', PreloadValues.vars_classes)
        zone = get_option('Select zone (optional)', PreloadValues.zones + ['Empty'])
        region = get_option('Select region (optional)', PreloadValues.regions + ['Empty'])
        cloud = get_option('Select cloud (optional)', PreloadValues.clouds + ['Empty'])
        service_type = get_option('Select service_type (optional)', PreloadValues.service_types + ['Empty'])
    except Exception as e:
        repr(e)
        return

    if name and value and type:
        node = URIRef(VAR_FORMAT.format(name=name, suffix=str(uuid.uuid1())))
        # add node
        graph.add((node, RDF.type, type))
        graph.add((node, VAR_NAME, Literal(name)))
        graph.add((node, VAR_VALUE, Literal(value)))

        if zone != 'Empty':
            graph.add((node, VAR_LOCATION, URIRef(TYPE_FORMAT.format(name=zone))))

        if region != 'Empty':
            graph.add((node, VAR_LOCATION, URIRef(TYPE_FORMAT.format(name=region))))

        if cloud != 'Empty':
            graph.add((node, VAR_LOCATION, URIRef(TYPE_FORMAT.format(name=region))))

        if service_type != 'Empty':
            graph.add((node, VAR_SERV_TYPE, URIRef(TYPE_FORMAT.format(name=service_type))))


def menu(input_file, output_file):
    print(f'Load ontology from {input_file}')
    graph = Graph()
    graph.parse(input_file, format='xml')
    print('Ontology loaded')

    print('Load dynamic properties')
    # preload values
    PreloadValues.service_types = _select_str_values_by_type(graph, 'ServiceType')
    print(f'Service Types: {PreloadValues.service_types}')

    PreloadValues.regions = _select_str_values_by_type(graph, 'Region')
    print(f'Regions: {PreloadValues.regions}')

    PreloadValues.clouds = _select_str_values_by_type(graph, 'Cloud')
    print(f'Clouds: {PreloadValues.service_types}')

    PreloadValues.zones = _select_str_values_by_type(graph, 'Zone')
    print(f'Zone: {PreloadValues.service_types}')

    PreloadValues.vars_classes = _select_subclasses(graph, 'Variable')
    print(f'Variable types: {PreloadValues.vars_classes}')
    print('Dynamic properties loaded')

    run = True
    while run:
        print(MENU_PROMPT)
        menu_item = int(input(">"))
        if menu_item == 1:
            get_variables_for_server(graph)
        elif menu_item == 2:
            get_all_variable_values(graph)
        elif menu_item == 3:
            add_variable(graph)
        elif menu_item == 4:
            save_file(graph, output_file)
        elif menu_item == 5:
            run = False


def usage():
    print('variables-ontology.py -i <inputfile> -o <outputfile>')


def main(argv):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "input=", "output="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output_file = 'variables-ontology-new.owl'
    input_file = 'variables-ontology.owl'
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--input"):
            input_file = a
        elif o in ("-o", "--output"):
            output_file = a
        else:
            assert False, "unhandled option"
    menu(input_file, output_file)


if __name__ == "__main__":
    main(sys.argv[1:])
