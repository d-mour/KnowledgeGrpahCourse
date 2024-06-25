from rdflib import Graph, Literal, RDF, URIRef, Namespace
# rdflib knows about quite a few popular namespaces, like W3C ontologies, schema.org etc.
from rdflib.namespace import FOAF , XSD, RDF, RDFS
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt

# Create a Graph
g = Graph()

# Create an RDF URI node to use as the subject for multiple triples
resource = Namespace("http://example.org/")

# Add triples using store's add() method.
g.add((resource['Resource'], RDF.type, RDFS.Resource))
g.add((resource['Resource'], RDFS.label, Literal('Resource')))
g.add((resource['Resource'], RDFS.isDefinedBy, resource['Text']))
g.add((resource['Resource'], RDFS.isDefinedBy, resource['Audio']))
g.add((resource['Resource'], RDFS.isDefinedBy, resource['Screenshot']))

g.add((resource['Text'], RDF.type, RDFS.Class))
g.add((resource['Text'], RDFS.subClassOf, resource['Resource']))
g.add((resource['Text'], RDFS.label, Literal('Text')))

g.add((resource['text_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['text_pr1'], RDFS.subClassOf, resource['Text']))
g.add((resource['text_pr1'], RDFS.label, Literal('yz near fort sterling like...')))
g.add((resource['text_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['text_pr2'], RDFS.subClassOf, resource['Text']))
g.add((resource['text_pr2'], RDFS.label, Literal('GO FARM T4 ORES AT PEN...')))
g.add((resource['text_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['text_pr3'], RDFS.subClassOf, resource['Text']))
g.add((resource['text_pr3'], RDFS.label, Literal('Yellow T5 - do cairn cloatch...')))

g.add((resource['Token'], RDFS.subClassOf, resource['Text']))
g.add((resource['Token'], RDFS.label, Literal('Token')))

g.add((resource['token_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['token_pr1'], RDFS.subClassOf, resource['Token']))
g.add((resource['token_pr1'], RDFS.label, Literal('[yz, near, fort, sterling,')))
g.add((resource['token_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['token_pr2'], RDFS.subClassOf, resource['Token']))
g.add((resource['token_pr2'], RDFS.label, Literal('[go, farm, t, ores,')))
g.add((resource['token_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['token_pr3'], RDFS.subClassOf, resource['Token']))
g.add((resource['token_pr3'], RDFS.label, Literal('[yellow, t, do, cairn,')))

g.add((resource['Lemma'], RDFS.subClassOf, resource['Token']))
g.add((resource['Lemma'], RDFS.label, Literal('Lemma')))

g.add((resource['lemma_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['lemma_pr1'], RDFS.subClassOf, resource['Lemma']))
g.add((resource['lemma_pr1'], RDFS.label, Literal('[yz, near, fort, sterling,')))
g.add((resource['lemma_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['lemma_pr2'], RDFS.subClassOf, resource['Lemma']))
g.add((resource['lemma_pr2'], RDFS.label, Literal('[go, farm, ores, pen,')))
g.add((resource['lemma_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['lemma_pr3'], RDFS.subClassOf, resource['Lemma']))
g.add((resource['lemma_pr3'], RDFS.label, Literal('[yellow, cairn, cloatch,')))

g.add((resource['POS'], RDFS.subClassOf, resource['Lemma']))
g.add((resource['POS'], RDFS.label, Literal('POS')))

g.add((resource['POS_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['POS_pr1'], RDFS.subClassOf, resource['POS']))
g.add((resource['POS_pr1'], RDFS.label, Literal('[(yz, NN), (near, IN),')))
g.add((resource['POS_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['POS_pr2'], RDFS.subClassOf, resource['POS']))
g.add((resource['POS_pr2'], RDFS.label, Literal('[(go, VB), (farm, NN),')))
g.add((resource['POS_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['POS_pr3'], RDFS.subClassOf, resource['POS']))
g.add((resource['POS_pr3'], RDFS.label, Literal('[(yellow, JJ), (cairn, NN),')))

g.add((resource['Audio'], RDF.type, RDFS.Class))
g.add((resource['Audio'], RDFS.subClassOf, resource['Resource']))
g.add((resource['Audio'], RDFS.label, Literal('Audio')))

g.add((resource['Audio_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['Audio_pr1'], RDFS.subClassOf, resource['Audio']))
g.add((resource['Audio_pr1'], RDFS.label, Literal('T3_ORE.mp3')))
g.add((resource['Audio_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['Audio_pr2'], RDFS.subClassOf, resource['Audio']))
g.add((resource['Audio_pr2'], RDFS.label, Literal('T5_WOOD.mp3')))
g.add((resource['Audio_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['Audio_pr3'], RDFS.subClassOf, resource['Audio']))
g.add((resource['Audio_pr3'], RDFS.label, Literal('T4_BLOCK.mp3')))

g.add((resource['Spectrogram'], RDFS.subClassOf, resource['Audio']))
g.add((resource['Spectrogram'], RDFS.label, Literal('Spectrogram')))

g.add((resource['spect_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['spect_pr1'], RDFS.subClassOf, resource['Spectrogram']))
g.add((resource['spect_pr1'], RDFS.label, Literal('spec3O.jpg')))
g.add((resource['spect_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['spect_pr2'], RDFS.subClassOf, resource['Spectrogram']))
g.add((resource['spect_pr2'], RDFS.label, Literal('spec5W.jpg')))
g.add((resource['spect_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['spect_pr3'], RDFS.subClassOf, resource['Spectrogram']))
g.add((resource['spect_pr3'], RDFS.label, Literal('spec4B.jpg')))

g.add((resource['MelSpectrogram'], RDFS.subClassOf, resource['Audio']))
g.add((resource['MelSpectrogram'], RDFS.label, Literal('MelSpectrogram')))

g.add((resource['melspect_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['melspect_pr1'], RDFS.subClassOf, resource['MelSpectrogram']))
g.add((resource['melspect_pr1'], RDFS.label, Literal('mels3O.jpg')))
g.add((resource['melspect_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['melspect_pr2'], RDFS.subClassOf, resource['MelSpectrogram']))
g.add((resource['melspect_pr2'], RDFS.label, Literal('mels5W.jpg')))
g.add((resource['melspect_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['melspect_pr3'], RDFS.subClassOf, resource['MelSpectrogram']))
g.add((resource['melspect_pr3'], RDFS.label, Literal('mels4B.jpg')))

g.add((resource['mfcc'], RDFS.subClassOf, resource['MelSpectrogram']))
g.add((resource['mfcc'], RDFS.label, Literal('mfcc')))

g.add((resource['mfcc_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['mfcc_pr1'], RDFS.subClassOf, resource['mfcc']))
g.add((resource['mfcc_pr1'], RDFS.label, Literal('[-1052.844238,-1052.844238]')))
g.add((resource['mfcc_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['mfcc_pr2'], RDFS.subClassOf, resource['mfcc']))
g.add((resource['mfcc_pr2'], RDFS.label, Literal('[0.000000,2.206847]')))
g.add((resource['mfcc_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['mfcc_pr3'], RDFS.subClassOf, resource['mfcc']))
g.add((resource['mfcc_pr3'], RDFS.label, Literal('[-3.404861,3.411330]')))

g.add((resource['Screenshot'], RDF.type, RDFS.Class))
g.add((resource['Screenshot'], RDFS.subClassOf, resource['Resource']))
g.add((resource['Screenshot'], RDFS.label, Literal('Screenshot')))

g.add((resource['Screen_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['Screen_pr1'], RDFS.subClassOf, resource['Screenshot']))
g.add((resource['Screen_pr1'], RDFS.label, Literal('ss11.jpg')))
g.add((resource['Screen_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['Screen_pr2'], RDFS.subClassOf, resource['Screenshot']))
g.add((resource['Screen_pr2'], RDFS.label, Literal('ss37.jpg')))
g.add((resource['Screen_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['Screen_pr3'], RDFS.subClassOf, resource['Screenshot']))
g.add((resource['Screen_pr3'], RDFS.label, Literal('ss22.jpg')))

g.add((resource['bbox'], RDFS.subClassOf, resource['Screenshot']))
g.add((resource['bbox'], RDFS.label, Literal('bbox')))

g.add((resource['bbox_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['bbox_pr1'], RDFS.subClassOf, resource['bbox']))
g.add((resource['bbox_pr1'], RDFS.label, Literal('[436.49769585253455,')))
g.add((resource['bbox_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['bbox_pr2'], RDFS.subClassOf, resource['bbox']))
g.add((resource['bbox_pr2'], RDFS.label, Literal('[867.0967741935482,]')))
g.add((resource['bbox_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['bbox_pr3'], RDFS.subClassOf, resource['bbox']))
g.add((resource['bbox_pr3'], RDFS.label, Literal('[213.08323563892148,')))

g.add((resource['img'], RDFS.subClassOf, resource['Screenshot']))
g.add((resource['img'], RDFS.label, Literal('img')))

g.add((resource['img_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['img_pr1'], RDFS.subClassOf, resource['img']))
g.add((resource['img_pr1'], RDFS.label, Literal('[img1.jpg, img2.jpg]')))
g.add((resource['img_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['img_pr2'], RDFS.subClassOf, resource['img']))
g.add((resource['img_pr2'], RDFS.label, Literal('[img1.jpg, img2.jpg]')))
g.add((resource['img_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['img_pr3'], RDFS.subClassOf, resource['img']))
g.add((resource['img_pr3'], RDFS.label, Literal('[img1.jpg, img2.jpg]')))

g.add((resource['grayscale'], RDFS.subClassOf, resource['img']))
g.add((resource['grayscale'], RDFS.label, Literal('grayscale')))

g.add((resource['gimg_pr1'], RDF.type, RDFS.Datatype))
g.add((resource['gimg_pr1'], RDFS.subClassOf, resource['grayscale']))
g.add((resource['gimg_pr1'], RDFS.label, Literal('[gimg1.jpg, gimg2.jpg]')))
g.add((resource['gimg_pr2'], RDF.type, RDFS.Datatype))
g.add((resource['gimg_pr2'], RDFS.subClassOf, resource['grayscale']))
g.add((resource['gimg_pr2'], RDFS.label, Literal('[gimg1.jpg, gimg2.jpg]')))
g.add((resource['gimg_pr3'], RDF.type, RDFS.Datatype))
g.add((resource['gimg_pr3'], RDFS.subClassOf, resource['grayscale']))
g.add((resource['gimg_pr3'], RDFS.label, Literal('[gimg1.jpg, gimg2.jpg]')))

g.serialize(destination="tbl.ttl")

q = """
    SELECT ?name
    WHERE {
        ?p rdfs:subClassOf <http://example.org/Resource> .
        ?p rdfs:label ?name .
    }    """

for r in g.query(q):
    print(r['name'])
