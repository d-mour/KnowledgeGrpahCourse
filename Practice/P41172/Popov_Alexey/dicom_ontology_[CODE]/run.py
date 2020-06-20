import os
import queries
from glob import glob
import rdflib
import pydicom
from rdflib import Graph, RDF, term, Literal

# requirements.txt file generation
status = True
if status:
    req_file = open('requirements.txt', 'w')
    req_file.write('pydicom ' + pydicom.__version__ + '\n')
    req_file.write('rdflib ' + rdflib.__version__ + '\n')

    req_file.close()

PREFIXES = ('prefix : <http://www.semanticweb.org/alexey/ontologies/2020/3/untitled-ontology-20>'
            'prefix owl: <http://www.w3.org/2002/07/owl#>'
            'prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>'
            'prefix xsd: <http://www.w3.org/2001/XMLSchema#>')

BASE = PREFIXES[10:82]
print('BASE: ', BASE)


def create_query(query, name=None):
    result = g.query(f'{PREFIXES}\n{query}')
    print(name if name else '')
    for row in result:
        print(row)


def load_images(path):
    return [pydicom.read_file(path + '/' + i) for i in os.listdir(path)]


g = Graph()
g.parse('dicom_ontology.owl', format='turtle')

print(f'Graph has {len(g)} statements.\n')
# print(g.serialize(format='turtle').decode('utf-8'))

print('**************************************Source Queries Begin*****************************************************')
create_query(queries.study_types, 'Study Types:')
create_query(queries.annotations, 'Annotations:')
create_query(queries.internal_organs, 'Internal Organs:')
create_query(queries.part_of_body, 'Part of Body:')
create_query(queries.annotated_scans, 'Annotated Scans:')
create_query(queries.not_annotated_scans, 'Not Annotated Scans:')
create_query(queries.localizer_scans, 'Localizer:')
create_query(queries.general_scans, 'General:')
create_query(queries.images_with_head, 'Images with Head:')
create_query(queries.images_with_neck, 'Images with Neck:')
create_query(queries.images_with_chest, 'Images with Chest:')
create_query(queries.images_with_abdomen, 'Images with Abdomen:')
create_query(queries.images_with_pelvis, 'Images with Pelvis:')
print('***************************************Source Queries End****************************************************\n')

data_path = 'annotated_images'
images = []

try:
    images = load_images(data_path)
    dicom_file_name = glob(data_path + '/*')
    print('Total of %d DICOM images.' % len(dicom_file_name))
except:
    print('Check value "data_path". If "data_path" is correct, then check the constraint. '
          'Most likely the images are not added. Add images.')

# ***************************************************Terms Begin********************************************************
# Classes
dicom_image = term.URIRef(BASE + 'DicomImage')

# Study Types
localizer = term.URIRef(BASE + 'Localizer')
general = term.URIRef(BASE + 'General')

# Annotation Status
annotated = term.URIRef(BASE + 'Annotated')
not_annotated = term.URIRef(BASE + 'NotAnnotated')

# Part of Body
head = term.URIRef(BASE + 'Head')
neck = term.URIRef(BASE + 'Neck')
chest = term.URIRef(BASE + 'Chest')
abdomen = term.URIRef(BASE + 'Abdomen')
pelvis = term.URIRef(BASE + 'Pelvis')

# Data Properties
name = term.URIRef(BASE + 'Name')
path = term.URIRef(BASE + 'Path')

# Object Property
has_LS_Annotation = term.URIRef(BASE + 'has_LS_Annotation')
# ****************************************************Terms End*********************************************************

index = 4
for image in images:
    index = index + 1
    img = term.URIRef(BASE + 'image_' + str(index))
    # Add dicom image
    g.add((img, RDF.type, dicom_image))
    if 'LOCALIZER' in str(image[0x0008, 0x0008]):
        # Add study type
        g.add((img, RDF.type, localizer))
    elif 'GENERAL' in str(image[0x0008, 0x0008]):
        g.add((img, RDF.type, general))
    # Add name
    g.add((img, name, Literal('CT_000' + str(index) + '.dcm')))
    # Add path
    g.add((img, name, Literal(data_path)))
    # Add annotation status
    try:
        image[0x6000, 0x0022] or image[0x6002, 0x0022] or image[0x6004, 0x0022] or \
        image[0x6006, 0x0022] or image[0x6008, 0x0022]
    except:
        g.add((img, RDF.type, not_annotated))

    # Add part of body
    try:
        if image[0x6000, 0x0022]:
            g.add((img, RDF.type, annotated))
            g.add((img, has_LS_Annotation, head))
        if image[0x6002, 0x0022]:
            g.add((img, RDF.type, annotated))
            g.add((img, has_LS_Annotation, neck))
        if image[0x6004, 0x0022]:
            g.add((img, RDF.type, annotated))
            g.add((img, has_LS_Annotation, chest))
        if image[0x6006, 0x0022]:
            g.add((img, RDF.type, annotated))
            g.add((img, has_LS_Annotation, abdomen))
        if image[0x6008, 0x0022]:
            g.add((img, RDF.type, annotated))
            g.add((img, has_LS_Annotation, pelvis))
    except:
        pass

print('*****************************************New Queries Begin*****************************************************')
create_query(queries.annotated_scans, 'Annotated Scans:')
create_query(queries.not_annotated_scans, 'Not Annotated Scans:')
create_query(queries.localizer_scans, 'Localizer:')
create_query(queries.general_scans, 'General:')
create_query(queries.images_with_head, 'Images with Head:')
create_query(queries.images_with_neck, 'Images with Neck:')
create_query(queries.images_with_chest, 'Images with Chest:')
create_query(queries.images_with_abdomen, 'Images with Abdomen:')
create_query(queries.images_with_pelvis, 'Images with Pelvis:')
print('******************************************New Queries End******************************************************')
