import pyshacl
from rdflib import Graph


def verify_graph(ontology_path, data_format, shapes_path):
    f1_graph = Graph().parse(ontology_path, format=data_format)
    f1_shapes = Graph().parse(shapes_path, format=data_format)
    results = pyshacl.validate(
        data_graph=f1_graph,
        shacl_graph=f1_shapes,
        data_graph_format=data_format,
        shacl_graph_format=data_format,
        inference="rdfs",
        debug=True,
        serialize_report_graph=data_format,
    )
    conforms, report_graph, report_text = results
    print(f"Conforms: {conforms}\nReport graph:\n{report_graph}")
