import json
from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

with open('data.json', encoding='utf-8') as json_file:
    data = json.load(json_file)

ns = Namespace('http://webprotege.stanford.edu/GuitarShop#')

g = Graph()
g.parse("GuitarShop.owl", format='turtle')


def add_data(data, category):
    if category == 'Manufacturers':
        for man in data[category]:
            name = URIRef(ns + man['Name'])
            url = Literal(man['Site'])
            country = Literal(man['Country'])
            info = Literal(man['Description'])

            g.add((name, RDF.type, OWL.NamedIndividual))
            g.add((name, RDF.type, ns.Manufacturer))
            if (name, RDFS.comment, None) not in g:
                g.add((name, RDFS.comment, info))
            if (name, RDFS.seeAlso, None) not in g:
                g.add((name, RDFS.seeAlso, url))
            # if (name,  RDFS.comment, country) not in g:
            #     g.add((name, RDFS.comment, country))

    if category == 'Guitars':
        for key in data[category].keys():
            strings_num = 6
            if key == 'Acoustic guitars':
                cls = ns.AcousticGuitar
            elif key == 'Classical guitars':
                cls = ns.ClassicalGuitar
            elif key == 'Electric guitars':
                cls = ns.ElectricGuitar
            elif key == 'Bass guitars':
                cls = ns.BassGuitar
                strings_num = 4
            for guitar in data[category][key]:
                name = guitar['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = ns + URIRef(name)
                price = Literal(guitar['Price'])
                brand = Literal(guitar['Brand'])
                color = Literal(guitar['Color'])
                pickup = Literal(guitar['Pickup'])
                strings = Literal(guitar['Strings'])
                if 'Strings number' in guitar.keys():
                    strings_num = Literal(guitar['Strings number'])
                strings_num = Literal(strings_num)

                g.add((name, RDF.type, OWL.NamedIndividual))
                g.add((name, RDF.type, cls))
                g.add((name, ns.hasManufacturer, URIRef(ns + brand)))
                g.add((name, ns.hasColor, color))
                g.add((name, ns.hasPickup, pickup))
                if (name, ns.hasPrice, None) in g:
                    g.set((name, ns.hasPrice, price))
                else:
                    g.add((name, ns.hasPrice, price))
                g.add((name, ns.hasStrings, strings))
                g.add((name, ns.numStrings, strings_num))

    if category == 'Amplifiers' or category == 'Bass amplifiers':
        for key in data[category].keys():
            if key == 'Combo':
                cls = ns.ComboAmplifier
                speakers_num = Literal(1)
            elif key == 'Heads':
                cls = ns.Head
            elif key == 'Preamplifiers':
                cls = ns.Preamplifier

            for amp in data[category][key]:
                name = amp['Name'].replace(' ', '_')
                for char in ['®', '#', ',', '`']:
                    name = name.replace(char, '')
                name = ns + URIRef(name)
                price = Literal(amp['Price'])
                brand = Literal(amp['Brand'].replace(' ', '_'))
                type = amp['Type']
                if type == 'transistor':
                    type = ns.Digital
                elif type == 'tube':
                    type = ns.Tube
                elif type == 'hybrid':
                    type = ns.Hybrid
                if 'Power' in amp.keys():
                    power = Literal(amp['Power'])
                if 'Speakers' in amp.keys():
                    speakers_num = Literal(amp['Speakers'])
                if key == 'Combo':
                    g.add((name, ns.numSpeakers, speakers_num))
                g.add((name, RDF.type, OWL.NamedIndividual))
                g.add((name, RDF.type, cls))
                g.add((name, ns.hasManufacturer, URIRef(ns + brand)))
                g.add((name, RDF.type, type))
                if 'Power' in amp.keys():
                    g.add((name, ns.hasPower, power))
                if (name, ns.hasPrice, None) in g:
                    g.set((name, ns.hasPrice, price))
                else:
                    g.add((name, ns.hasPrice, price))
                if category == 'Bass amplifiers':
                    g.add((name, RDF.type, ns.BassAmplifier))

    if category == 'Pickups':
        for pickup in data[category]:
            name = pickup['Name'].replace(' ', '_')
            for char in ['®', '#', ',', '`']:
                name = name.replace(char, '')
            name = ns + URIRef(name)
            price = Literal(pickup['Price'])
            brand = Literal(pickup['Brand'].replace(' ', '_'))
            type = Literal(pickup['Type'])
            active = pickup['Active']
            use = pickup['Use']

            g.add((name, RDF.type, OWL.NamedIndividual))
            if active:
                g.add((name, RDF.type, ns.Active))
            else:
                g.add((name, RDF.type, ns.Passive))
            g.add((name, ns.hasManufacturer, URIRef(ns + brand)))
            g.add((name, ns.hasType, type))
            if use == 'electric':
                g.add((name, ns.isSuitableFor, ns.ElectricGuitar))
            elif use == 'bass':
                g.add((name, ns.isSuitableFor, ns.BassGuitar))
            if (name, ns.hasPrice, None) in g:
                g.set((name, ns.hasPrice, price))
            else:
                g.add((name, ns.hasPrice, price))

    if category == 'Strings':
        for strings in data[category]:
            name = strings['Name'].replace(' ', '_')
            for char in ['®', '#', ',', '`']:
                name = name.replace(char, '')
            name = ns + URIRef(name)
            price = Literal(strings['Price'])
            brand = Literal(strings['Brand'].replace(' ', '_'))
            material = Literal(strings['Material'])
            gauge = Literal(strings['Gauge'])
            use = strings['Use']
            number = Literal(strings['Number'])

            g.add((name, RDF.type, OWL.NamedIndividual))
            g.add((name, ns.hasManufacturer, URIRef(ns + brand)))
            g.add((name, ns.hasMaterial, material))
            g.add((name, ns.hasGauge, gauge))
            if use == 'electric':
                g.add((name, ns.isSuitableFor, ns.ElectricGuitar))
            elif use == 'acoustic':
                g.add((name, ns.isSuitableFor, ns.AcousticGuitar))
            elif use == 'classical':
                g.add((name, ns.isSuitableFor, ns.ClassicalGuitar))
            elif use == 'bass':
                g.add((name, ns.isSuitableFor, ns.BassGuitar))
            if (name, ns.hasPrice, None) in g:
                g.set((name, ns.hasPrice, price))
            else:
                g.add((name, ns.hasPrice, price))


add_data(data, 'Manufacturers')
add_data(data, 'Guitars')
add_data(data, 'Amplifiers')
add_data(data, 'Bass amplifiers')
add_data(data, 'Pickups')
add_data(data, 'Strings')

print(g.serialize(format="turtle").decode("utf-8"))

g.serialize(destination='GuitarShopModified.owl', format='turtle')
