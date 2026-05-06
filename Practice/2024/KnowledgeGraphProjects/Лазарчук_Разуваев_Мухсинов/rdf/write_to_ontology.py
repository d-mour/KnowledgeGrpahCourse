import pandas as pd
import numpy as np
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

cars = pd.read_csv('resource/new_cars.csv')

car_columns = ['Company', 'Model', 'Variant', 'Seating_Capacity', 'Ex-Price', 'Fuel_Type', 'Wheelbase', 'Price_Category', 'Offroad_Capability', 'Car_Dimensions', 'Appearance', 'Electronics_&_Comfort', 'Engine', 'Safety', 'Suspensions_&_Brakes', 'Transmission']
appearance_columns = ['Length', 'Width', 'Height', 'Boot_Space', 'Doors', 'Ground_Clearance', 'Kerb_Weight']
electronics_and_comfort_columns = ['Cruise_Control', 'Power_Steering']
engine_columns = ['Displacement', 'Power', 'Torque']
safety_columns = ['ABS', 'Airbags']
suspensions_and_brakes_columns = ['Front_Brakes', 'Front_Suspension', 'Rear_Brakes', 'Rear_Suspension']
transmission_columns = ['Drivetrain', 'Gears']

appearance_array = cars[appearance_columns].dropna(how='all').drop_duplicates()
electronics_and_comfort_array = cars[electronics_and_comfort_columns].dropna(how='all').drop_duplicates()
engine_array = cars[engine_columns].dropna(how='all').drop_duplicates()
safety_array = cars[safety_columns].dropna(how='all').drop_duplicates()
suspensions_and_brakes_array = cars[suspensions_and_brakes_columns].dropna(how='all').drop_duplicates()
transmission_array = cars[transmission_columns].dropna(how='all').drop_duplicates()

cars_array = []

appearance_list = appearance_array.values.tolist()
electronics_list = electronics_and_comfort_array.values.tolist()
engines_list = engine_array.values.tolist()
safety_list = safety_array.values.tolist()
suspensions_list = suspensions_and_brakes_array.values.tolist()
transmission_list = transmission_array.values.tolist()

for _, row in cars.iterrows():
    appearance_index = -1
    for i in range (0, len(appearance_list)):
        if row['Length'] == appearance_list[i][0] and row['Width'] == appearance_list[i][1] and row['Height'] == appearance_list[i][2] and row['Boot_Space'] == appearance_list[i][3] and row['Doors'] == appearance_list[i][4] and row['Ground_Clearance'] == appearance_list[i][5] and row['Kerb_Weight'] == appearance_list[i][6]:
            appearance_index = i
            break
    electronics_index = -1
    for i in range (0, len(electronics_list)):
        if row['Cruise_Control'] == electronics_list[i][0] and row['Power_Steering'] == electronics_list[i][1]:
            electronics_index = i
            break
    engine_index = -1
    for i in range (0, len(engines_list)):
        if row['Displacement'] == engines_list[i][0] and row['Power'] == engines_list[i][1] and row['Torque'] == engines_list[i][2]:
            engine_index = i
            break
    safety_index = -1
    for i in range (0, len(safety_list)):
        if row['ABS'] == safety_list[i][0] and row['Airbags'] == safety_list[i][1]:
            safety_index = i
            break
    suspension_index = -1
    for i in range (0, len(suspensions_list)):
        if row['Front_Brakes'] == suspensions_list[i][0] and row['Front_Suspension'] == suspensions_list[i][1] and row['Rear_Brakes'] == suspensions_list[i][2] and row['Rear_Suspension'] == suspensions_list[i][3]:
            suspension_index = i
            break
    transmission_index = -1
    for i in range (0, len(transmission_list)):
        if row['Drivetrain'] == transmission_list[i][0] and row['Gears'] == transmission_list[i][1]:
            transmission_index = i
            break

    car_data = row[[
        'Company', 'Model', 'Variant', 'Seating_Capacity', 'Price', 'Fuel_Type', 'Wheelbase', 'Price_Category',
        'Offroad_Capability', 'Car_Dimensions']].to_dict()

    car_data['Appearance'] = appearance_index
    car_data['Electronics_&_Comfort'] = electronics_index
    car_data['Engine'] = engine_index
    car_data['Safety'] = safety_index
    car_data['Suspensions_&_Brakes'] = suspension_index
    car_data['Transmission'] = transmission_index

    cars_array.append(car_data)

g = Graph()
g.parse("ontolody.rdf", format="xml")
ontology_ns = Namespace("http://www.semanticweb.org/andrew/ontologies/2024/10/untitled-ontology-13#")
g.bind("", ontology_ns)

for i in range (0, len(appearance_list)):
    appearance_instance = URIRef(ontology_ns + "Appearance_" + str(i))
    g.add((appearance_instance, RDF.type, ontology_ns.Appearance))
    g.add((appearance_instance, ontology_ns.hasBootSpace, Literal(appearance_list[i][3], datatype=XSD.float)))
    g.add((appearance_instance, ontology_ns.hasDoors, Literal(appearance_list[i][4], datatype=XSD.float)))
    g.add((appearance_instance, ontology_ns.hasGroundClearance, Literal(appearance_list[i][5], datatype=XSD.float)))
    g.add((appearance_instance, ontology_ns.hasHeight, Literal(appearance_list[i][2], datatype=XSD.float)))
    g.add((appearance_instance, ontology_ns.hasWidth, Literal(appearance_list[i][1], datatype=XSD.float)))
    g.add((appearance_instance, ontology_ns.hasLength, Literal(appearance_list[i][0], datatype=XSD.float)))
    g.add((appearance_instance, ontology_ns.hasKerbWeight, Literal(appearance_list[i][6], datatype=XSD.float)))

for i in range (0, len(electronics_list)):
    ec_instance = URIRef(ontology_ns + "Electronics_&_Comfort_" + str(i))
    electronics_comfort_class = URIRef(ontology_ns + "Electronics_&_Comfort")
    g.add((ec_instance, RDF.type, electronics_comfort_class))
    g.add((ec_instance, ontology_ns.hasPowerSteering, Literal(electronics_list[i][1], datatype=XSD.boolean)))
    g.add((ec_instance, ontology_ns.hasCruiseControl, Literal(electronics_list[i][0], datatype=XSD.boolean)))

for i in range (0, len(safety_list)):
    safety_instance = URIRef(ontology_ns + "Safety_" + str(i))
    g.add((safety_instance, RDF.type, ontology_ns.Safety))
    g.add((safety_instance, ontology_ns.hasABS, Literal(safety_list[i][0], datatype=XSD.boolean)))
    g.add((safety_instance, ontology_ns.hasAirbags, Literal(safety_list[i][1], datatype=XSD.boolean)))

for i in range (0, len(transmission_list)):
    transmission_instance = URIRef(ontology_ns + "Transmission_" + str(i))
    g.add((transmission_instance, RDF.type, ontology_ns.Transmission))
    g.add((transmission_instance, ontology_ns.hasDrivetrain, Literal(transmission_list[i][0], datatype=XSD.string)))
    g.add((transmission_instance, ontology_ns.hasGears, Literal(transmission_list[i][1], datatype=XSD.float)))

for i in range (0, len(engines_list)):
    engine_instance = URIRef(ontology_ns + "Engine_" + str(i))
    g.add((engine_instance, RDF.type, ontology_ns.Engine))
    g.add((engine_instance, ontology_ns.hasDisplacement, Literal(engines_list[i][0], datatype=XSD.float)))
    g.add((engine_instance, ontology_ns.hasPower, Literal(engines_list[i][1], datatype=XSD.float)))
    g.add((engine_instance, ontology_ns.hasTorque, Literal(engines_list[i][2], datatype=XSD.float)))

for i in range (0, len(suspensions_list)):
    sb_instance = URIRef(ontology_ns + "Suspension_&_Brakes_" + str(i))
    suspensions_brakes_class = URIRef(ontology_ns + "Suspension_&_Brakes")
    g.add((sb_instance, RDF.type, suspensions_brakes_class))
    g.add((sb_instance, ontology_ns.hasFrontBrakes, Literal(suspensions_list[i][0], datatype=XSD.string)))
    g.add((sb_instance, ontology_ns.hasRearBrakes, Literal(suspensions_list[i][2], datatype=XSD.string)))
    g.add((sb_instance, ontology_ns.hasFrontSuspension, Literal(suspensions_list[i][1], datatype=XSD.string)))
    g.add((sb_instance, ontology_ns.hasRearSuspension, Literal(suspensions_list[i][3], datatype=XSD.string)))

for i in range (0, len(cars_array)):
    car_instance = URIRef(ontology_ns + "Car_" + str(i))
    g.add((car_instance, RDF.type, ontology_ns.Car))
    g.add((car_instance, ontology_ns.hasMake, Literal(cars_array[i]['Company'], datatype=XSD.string)))
    g.add((car_instance, ontology_ns.hasModel, Literal(cars_array[i]['Model'], datatype=XSD.string)))
    g.add((car_instance, ontology_ns.hasVariant, Literal(cars_array[i]['Variant'], datatype=XSD.string)))
    g.add((car_instance, ontology_ns.hasSeatingCapacity, Literal(cars_array[i]['Seating_Capacity'], datatype=XSD.float)))
    g.add((car_instance, ontology_ns.hasExShowroomPrice, Literal(cars_array[i]['Price'], datatype=XSD.float)))
    g.add((car_instance, ontology_ns.hasFuelType, Literal(cars_array[i]['Fuel_Type'], datatype=XSD.string)))
    g.add((car_instance, ontology_ns.hasWheelbase, Literal(cars_array[i]['Wheelbase'], datatype=XSD.float)))
    g.add((car_instance, ontology_ns.hasPriceCategory, Literal(cars_array[i]['Price_Category'], datatype=XSD.string)))
    g.add((car_instance, ontology_ns.hasOffroadCapability, Literal(cars_array[i]['Offroad_Capability'], datatype=XSD.string)))
    g.add((car_instance, ontology_ns.hasDimension, Literal(cars_array[i]['Car_Dimensions'], datatype=XSD.string)))
    appearance_ref = URIRef(ontology_ns + "Appearance_" + str(cars_array[i]['Appearance']))
    g.add((car_instance, ontology_ns.hasAppearance, appearance_ref))
    engine_ref = URIRef(ontology_ns + "Engine_" + str(cars_array[i]['Engine']))
    g.add((car_instance, ontology_ns.hasEngine, engine_ref))
    transmission_ref = URIRef(ontology_ns + "Transmission_" + str(cars_array[i]['Transmission']))
    g.add((car_instance, ontology_ns.hasTransmission, transmission_ref))
    safety_ref = URIRef(ontology_ns + "Safety_" + str(cars_array[i]['Safety']))
    g.add((car_instance, ontology_ns.hasSafety, safety_ref))
    ec_ref = URIRef(ontology_ns + "Electronics_&_Comfort_" + str(cars_array[i]['Electronics_&_Comfort']))
    g.add((car_instance, ontology_ns.hasElectronicsAndComfort, ec_ref))
    sb_ref = URIRef(ontology_ns + "Suspension_&_Brakes_" + str(cars_array[i]['Suspensions_&_Brakes']))
    g.add((car_instance, ontology_ns.hasSuspensionAndBrakes, sb_ref))

# print(cars_array[0])
g.serialize(destination="updated_ontology.owl", format="xml")
print("Данные успешно добавлены!")