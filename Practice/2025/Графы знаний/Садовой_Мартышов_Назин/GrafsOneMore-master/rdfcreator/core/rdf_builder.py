from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from typing import Dict, List, Any
from ..utils.transformers import normalize_string

def build_rdf(data: Dict[str, Any], output_path: str, debug: bool = False):
    g = Graph()
    
    
    ex = Namespace("http://example.org/ontology/")
    g.bind("ex", ex)
    
    
    g.add((ex.ontology, RDF.type, OWL.Ontology))
    
    if debug:
        print("DEBUG: Starting RDF construction")
        print(f"DEBUG: Processing {len(data['rows'])} rows from {len(data['files_processed'])} files")
    
    instance_count = 0
    relation_count = 0
    
    
    all_classes = set()
    property_info = {}  
    
    
    all_instances = {}
    
    for row in data['rows']:
        
        for class_name in row['classes'].keys():
            all_classes.add(class_name)
        
        
        for attribute in row['attributes']:
            prop_name = attribute['name']
            class_to = attribute['class-to']
            class_from = attribute['class-from']
            
            if prop_name not in property_info:
                property_info[prop_name] = {
                    'domain': class_to,
                    'range': class_from
                }
        
        
        for class_name, properties in row['classes'].items():
            if not properties:
                continue
            
            
            all_values = []
            for prop_name, prop_value in properties.items():
                if isinstance(prop_value, list):
                    all_values.extend(prop_value)
                else:
                    all_values.append(prop_value)
            
            
            for value in all_values:
                if not value or value == 'NULL':
                    continue
                
                
                instance_uri = ex[value]
                
                
                g.add((instance_uri, RDF.type, ex[class_name]))
                
                
                g.add((instance_uri, ex["name"], Literal(value)))
                
                
                key = f"{class_name}:{value}"
                all_instances[key] = instance_uri
                
                instance_count += 1
                
                if debug and data['rows'].index(row) == 0:
                    print(f"DEBUG: Created instance {instance_uri} of type {class_name} with value '{value}'")
    
    
    for class_name in all_classes:
        class_uri = ex[class_name]
        g.add((class_uri, RDF.type, OWL.Class))
        if debug:
            print(f"DEBUG: Declared class {class_uri}")
    
    
    if 'hierarchy' in data:
        hierarchy = data['hierarchy']
        for hierarchy_item in hierarchy:
            if 'class' in hierarchy_item and 'subclasses' in hierarchy_item:
                parent_class = hierarchy_item['class']
                subclasses = hierarchy_item['subclasses']
                
                
                if parent_class == 'root':
                    parent_uri = OWL.Thing
                    
                    for subclass in subclasses:
                        subclass_uri = ex[subclass]
                        
                        
                        if subclass not in all_classes:
                            g.add((subclass_uri, RDF.type, OWL.Class))
                            all_classes.add(subclass)
                            if debug:
                                print(f"DEBUG: Declared subclass {subclass_uri}")
                        
                        
                        g.add((subclass_uri, RDFS.subClassOf, parent_uri))
                        
                        if debug:
                            print(f"DEBUG: Added hierarchy: {subclass_uri} rdfs:subClassOf {parent_uri}")
                else:
                    
                    parent_uri = ex[parent_class]
                    
                    
                    if parent_class not in all_classes:
                        g.add((parent_uri, RDF.type, OWL.Class))
                        all_classes.add(parent_class)
                        if debug:
                            print(f"DEBUG: Declared parent class {parent_uri}")
                    
                    for subclass in subclasses:
                        subclass_uri = ex[subclass]
                        
                        
                        if subclass not in all_classes:
                            g.add((subclass_uri, RDF.type, OWL.Class))
                            all_classes.add(subclass)
                            if debug:
                                print(f"DEBUG: Declared subclass {subclass_uri}")
                        
                        
                        g.add((subclass_uri, RDFS.subClassOf, parent_uri))
                        
                        if debug:
                            print(f"DEBUG: Added hierarchy: {subclass_uri} rdfs:subClassOf {parent_uri}")
    
    
    
    used_properties = set()
    for row in data['rows']:
        for attribute in row['attributes']:
            used_properties.add(attribute['name'])
    
    for prop_name in used_properties:
        prop_uri = ex[prop_name]
        g.add((prop_uri, RDF.type, OWL.ObjectProperty))
        
        
        if prop_name in property_info:
            domain_class = property_info[prop_name]['domain']
            range_class = property_info[prop_name]['range']
            
            domain_uri = ex[domain_class]
            range_uri = ex[range_class]
            
            g.add((prop_uri, RDFS.domain, domain_uri))
            g.add((prop_uri, RDFS.range, range_uri))
            
            if debug:
                print(f"DEBUG: Declared property {prop_uri} with domain {domain_uri} and range {range_uri}")
    
    
    for row in data['rows']:
        
        for attribute in row['attributes']:
            attribute_name = attribute['name']
            class_to = attribute['class-to']
            class_from = attribute['class-from']
            values = attribute['values']
            
            if debug and data['rows'].index(row) == 0:
                print(f"DEBUG: Processing attribute {attribute_name}: {class_to} -> {class_from} with values {values}")
            
            
            if not isinstance(values, list):
                values = [values]
            
            
            
            to_instance_value = None
            if class_to in row['classes']:
                
                for prop_name, prop_value in row['classes'][class_to].items():
                    if isinstance(prop_value, list) and prop_value:
                        to_instance_value = prop_value[0]
                        break
                    elif isinstance(prop_value, str):
                        to_instance_value = prop_value
                        break
            
            if not to_instance_value:
                if debug and data['rows'].index(row) == 0:
                    print(f"DEBUG: No instance found for class {class_to} in current row")
                continue
            
            
            to_instance_key = f"{class_to}:{to_instance_value}"
            if to_instance_key not in all_instances:
                if debug and data['rows'].index(row) == 0:
                    print(f"DEBUG: Instance URI not found for {to_instance_key}")
                continue
            
            to_instance_uri = all_instances[to_instance_key]
            
            
            for from_value in values:
                from_instance_key = f"{class_from}:{from_value}"
                if from_instance_key in all_instances:
                    from_instance_uri = all_instances[from_instance_key]
                    
                    
                    relation_uri = ex[attribute_name]
                    g.add((to_instance_uri, relation_uri, from_instance_uri))
                    relation_count += 1
                    
                    if debug and data['rows'].index(row) == 0:
                        print(f"DEBUG: Created relation {to_instance_uri} {relation_uri} {from_instance_uri}")
                else:
                    if debug and data['rows'].index(row) == 0:
                        print(f"DEBUG: Instance not found for class {class_from} with value {from_value}")
    
    
    g.serialize(destination=output_path, format='xml', encoding='utf-8')
    print(f"RDF ontology saved to {output_path}")
    print(f"Created {len(all_classes)} classes, {instance_count} instances and {relation_count} object property relations")
    print(f"Processed files: {', '.join(data['files_processed'])}")