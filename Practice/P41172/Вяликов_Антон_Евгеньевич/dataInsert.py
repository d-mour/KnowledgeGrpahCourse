import json
from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL


with open('dataToInsert.json', encoding='utf-8') as json_file:
    data = json.load(json_file)

namespace = Namespace('http://www.semanticweb.org/avyal/ontologies/2020/5/untitled-ontology-3#')

graph = Graph()
graph.parse("AutoAftermarketPartsOntology.owl", format='turtle')

"""
This method inserts data to ontology by parsing json file. 
"""
def insert_data(data, category):
    if category == 'Manufacturers':
        for man in data[category]:
            name = URIRef(namespace + man['Name'])
            url = Literal(man['Website'])
            country = Literal(man['Country'])
            info = Literal(man['Description'])

            graph.add((name, RDF.type, OWL.NamedIndividual))
            graph.add((name, RDF.type, namespace.Manufacturers))
            if (name, RDFS.comment, None) not in graph:
                graph.add((name, RDFS.comment, info))
                graph.add((name, RDFS.comment, country))
            if (name, RDFS.seeAlso, None) not in graph:
                graph.add((name, RDFS.seeAlso, url))

    if category == 'Body':
        for key in data[category].keys():
            if key == 'Bumpers':
                cls = namespace.Bumpers
            elif key == 'Body_kits':
                cls = namespace.Body_kits
            elif key == 'Body_kits':
                cls = namespace.Wings
            elif key == 'Side_skirts':
                cls = namespace.Side_skirts
            elif key == 'Hoods':
                cls = namespace.Hoods
            elif key == 'Wings':
                cls = namespace.Wings

            #Iterating through keys and assign required vars
            for body in data[category][key]:
                name = body['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = namespace + URIRef(name)
                price = Literal(body['Price'])
                manufacturer = Literal(body['Manufacturer'])
                if 'CompatibleWithCar' in body.keys():
                    cwc = Literal(body['CompatibleWithCar'])
                if 'Material' in body.keys():
                    material = Literal(body['Material'])

                #Add found data to ontology
                graph.add((name, RDF.type, OWL.NamedIndividual))
                graph.add((name, RDF.type, cls))
                graph.add((name, namespace.hasManufacturer, URIRef(namespace + manufacturer)))
                if 'CompatibleWithCar' in body.keys():
                    graph.add((name, namespace.compatibleWithCar, cwc))
                if 'Material' in body.keys():
                    graph.add((name, namespace.hasMaterial, material))
                if (name, namespace.hasPrice, None) in graph:
                    graph.set((name, namespace.hasPrice, price))
                else:
                    graph.add((name, namespace.hasPrice, price))

    if category == 'Brake_system':
        for key in data[category].keys():
            if key == 'Brake_disks':
                cls = namespace.Brake_disks
            elif key == 'Brake_pads':
                cls = namespace.Brake_pads
            elif key == 'Calipers':
                cls = namespace.Calipers

            for bs in data[category][key]:
                name = bs['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = namespace + URIRef(name)
                price = Literal(bs['Price'])
                manufacturer = Literal(bs['Manufacturer'].replace(' ', '_'))
                if 'Material' in bs.keys():
                    material = Literal(bs['Material'])
                if 'ForPublicRoad' in bs.keys():
                    fpr = Literal(bs['ForPublicRoad'])

                graph.add((name, RDF.type, OWL.NamedIndividual))
                graph.add((name, RDF.type, cls))
                graph.add((name, namespace.hasManufacturer, URIRef(namespace + manufacturer)))
                if 'Material' in bs.keys():
                    graph.add((name, namespace.hasMaterial, material))
                if 'ForPublicRoad' in bs.keys():
                    graph.add((name, namespace.forPublicRoad, fpr))
                if (name, namespace.hasPrice, None) in graph:
                    graph.set((name, namespace.hasPrice, price))
                else:
                    graph.add((name, namespace.hasPrice, price))

    if category == 'Engine':
        for key in data[category].keys():
            if key == 'ECU':
                cls = namespace.ECU
            elif key == 'Exhaust_systems':
                cls = namespace.Exhaust_systems
            elif key == 'Fuel_systems':
                cls = namespace.Fuel_systems
            elif key == 'Intake_systems':
                cls = namespace.Intake_systems
            elif key == 'Stroker_kits':
                cls = namespace.Stroker_kits
            elif key == 'Turbochargers':
                cls = namespace.Turbochargers

            for engine in data[category][key]:
                name = engine['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = namespace + URIRef(name)
                price = Literal(engine['Price'])
                manufacturer = Literal(engine['Manufacturer'].replace(' ', '_'))
                if 'CompatibleWithEngine' in engine.keys():
                    cwe = Literal(engine['CompatibleWithEngine'])
                if 'CalculatedPotential' in engine.keys():
                    potential = Literal(engine['CalculatedPotential'])
                if 'Material' in engine.keys():
                    material = Literal(engine['Material'])

                graph.add((name, RDF.type, OWL.NamedIndividual))
                print(name, RDF.type, cls)
                graph.add((name, RDF.type, cls))
                print(name, namespace.hasManufacturer, URIRef(namespace + manufacturer))
                graph.add((name, namespace.hasManufacturer, URIRef(namespace + manufacturer)))
                if 'Material' in engine.keys():
                    graph.add((name, namespace.hasMaterial, material))
                if 'CompatibleWithEngine' in engine.keys():
                    graph.add((name, namespace.compatibleWithEngine, cwe))
                if 'CalculatedPotential' in engine.keys():
                    graph.add((name, namespace.hasCalculatedPotential, potential))
                if (name, namespace.hasPrice, None) in graph:
                    graph.set((name, namespace.hasPrice, price))
                else:
                    graph.add((name, namespace.hasPrice, price))

    if category == 'Interior':
        for key in data[category].keys():
            if key == 'Roll_cages':
                cls = namespace.Roll_cages
            elif key == 'Seats':
                cls = namespace.Seats
            elif key == 'Steering_wheels':
                cls = namespace.Steering_wheels

            for seat in data[category][key]:
                name = seat['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = namespace + URIRef(name)
                price = Literal(seat['Price'])
                manufacturer = Literal(seat['Manufacturer'].replace(' ', '_'))
                if 'CompatibleWithCar' in seat.keys():
                    cwc = Literal(seat['CompatibleWithCar'])
                if 'ForPublicRoad' in seat.keys():
                    fpr = Literal(seat['ForPublicRoad'])

                graph.add((name, RDF.type, OWL.NamedIndividual))
                graph.add((name, RDF.type, cls))
                graph.add((name, namespace.hasManufacturer, URIRef(namespace + manufacturer)))
                if 'CompatibleWithCar' in seat.keys():
                    graph.add((name, namespace.compatibleWithCar, cwc))
                if 'ForPublicRoad' in seat.keys():
                    graph.add((name, namespace.forPublicRoad, fpr))
                if (name, namespace.hasPrice, None) in graph:
                    graph.set((name, namespace.hasPrice, price))
                else:
                    graph.add((name, namespace.hasPrice, price))
    
    if category == 'Suspension':
        for key in data[category].keys():
            if key == 'Anti_roll_bars':
                cls = namespace.Anti_roll_bars
            elif key == 'Body_stiffness':
                cls = namespace.Body_stiffness
            elif key == 'Springs_and_shock_absorbers':
                cls = namespace.Springs_and_shock_absorbers

            for spring in data[category][key]:
                name = spring['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = namespace + URIRef(name)
                price = Literal(spring['Price'])
                manufacturer = Literal(spring['Manufacturer'].replace(' ', '_'))

                graph.add((name, RDF.type, OWL.NamedIndividual))
                graph.add((name, RDF.type, cls))
                graph.add((name, namespace.hasManufacturer, URIRef(namespace + manufacturer)))
                if (name, namespace.hasPrice, None) in graph:
                    graph.set((name, namespace.hasPrice, price))
                else:
                    graph.add((name, namespace.hasPrice, price))
                
    if category == 'Transmission':
        for key in data[category].keys():
            if key == 'Clutches':
                cls = namespace.Clutches
            elif key == 'Driveshafts':
                cls = namespace.Driveshafts

            for clutch in data[category][key]:
                name = clutch['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = namespace + URIRef(name)
                price = Literal(clutch['Price'])
                manufacturer = Literal(clutch['Manufacturer'].replace(' ', '_'))
                material = Literal(clutch['Material'])

                graph.add((name, RDF.type, OWL.NamedIndividual))
                graph.add((name, RDF.type, cls))
                graph.add((name, namespace.hasManufacturer, URIRef(namespace + manufacturer)))
                graph.add((name, namespace.hasMaterial, material))
                if (name, namespace.hasPrice, None) in graph:
                    graph.set((name, namespace.hasPrice, price))
                else:
                    graph.add((name, namespace.hasPrice, price))

    if category == 'Wheels':
        for key in data[category].keys():
            if key == 'Rims':
                cls = namespace.Rims
            elif key == 'Tires':
                cls = namespace.Tires

            for wheel in data[category][key]:
                name = wheel['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = namespace + URIRef(name)
                price = Literal(wheel['Price'])
                manufacturer = Literal(wheel['Manufacturer'].replace(' ', '_'))
                if 'Type' in wheel.keys():
                    wheelType = Literal(wheel['Type'])
                if 'Size' in wheel.keys():
                    size = Literal(wheel['Size'])
                if 'MaxSpeed' in wheel.keys():
                    maxSpeed = Literal(wheel['MaxSpeed'])
                if 'ForPublicRoad' in wheel.keys():
                    fpr = Literal(wheel['ForPublicRoad'])

                graph.add((name, RDF.type, OWL.NamedIndividual))
                graph.add((name, RDF.type, cls))
                graph.add((name, namespace.hasManufacturer, URIRef(namespace + manufacturer)))
                if 'Type' in wheel.keys():
                    graph.add((name, namespace.hasType, wheelType))
                if 'Size' in wheel.keys():
                    graph.add((name, namespace.hasSize, size))
                if 'MaxSpeed' in wheel.keys():
                    graph.add((name, namespace.hasMaxSpeed, maxSpeed))
                if 'ForPublicRoad' in wheel.keys():
                    graph.add((name, namespace.forPublicRoad, fpr))
                if (name, namespace.hasPrice, None) in graph:
                    graph.set((name, namespace.hasPrice, price))
                else:
                    graph.add((name, namespace.hasPrice, price))

#Insert data by categories
insert_data(data, 'Manufacturers')
insert_data(data, 'Body')
insert_data(data, 'Brake_system')
insert_data(data, 'Engine')
insert_data(data, 'Interior')
insert_data(data, 'Suspension')
insert_data(data, 'Transmission')
insert_data(data, 'Wheels')

print(graph.serialize(format="turtle").decode("utf-8"))

graph.serialize(destination='AftermarketPartsOntologyFull.owl', format='turtle')
