import csv
from pathlib import Path
from typing import Dict, List, Any
from ..utils.transformers import apply_transformations, normalize_string

def process_csv_files(config: Dict[str, Any], debug: bool = False) -> Dict[str, Any]:
    base_path = Path('parsed_csv')
    
    global_transformations = config.get('global_transformations', [])
    hierarchy = config.get('hierarchy', [])
    
    if debug:
        print(f"DEBUG: Global transformations: {global_transformations}")
        print(f"DEBUG: Hierarchy: {hierarchy}")
        print(f"DEBUG: Files to process: {[f['file'] for f in config.get('files', [])]}")
    
    
    all_data = {
        'rows': [],  
        'class_definitions': {},  
        'files_processed': [],  
        'hierarchy': hierarchy  
    }
    
    
    for file_config in config.get('files', []):
        for parse_config in file_config['parse']:
            if parse_config['type'] == 'class':
                class_name = parse_config['class']
                if class_name not in all_data['class_definitions']:
                    all_data['class_definitions'][class_name] = {}
                
                
                for col_config in parse_config['columns']:
                    col_name = col_config['column']
                    all_data['class_definitions'][class_name][col_name] = {
                        'transformations': col_config.get('transformations', [])
                    }
    
    
    for file_config in config.get('files', []):
        file_path = base_path / file_config['file']
        
        if debug:
            print(f"DEBUG: Processing file {file_path}")
        
        if not file_path.exists():
            print(f"Warning: File {file_path} not found. Skipping.")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if debug:
            print(f"DEBUG: Read {len(rows)} rows from {file_config['file']}")
            if rows:
                print(f"DEBUG: First row: {rows[0]}")
        
        for i, row in enumerate(rows):
            if debug and i == 0:
                print(f"DEBUG: Processing first row: {row}")
                
            processed_row = {
                'source_file': file_config['file'],
                'classes': {},
                'attributes': []
            }
            
            
            for parse_config in file_config['parse']:
                if parse_config['type'] == 'class':
                    class_name = parse_config['class']
                    processed_row['classes'][class_name] = {}
                    
                    if debug and i == 0:
                        print(f"DEBUG: Processing class {class_name}")
                    
                    for col_config in parse_config['columns']:
                        col_name = col_config['column']
                        if col_name not in row:
                            if debug and i == 0:
                                print(f"DEBUG: Column {col_name} not found in row")
                            continue
                            
                        value = row[col_name].strip()
                        if not value or value == 'NULL':
                            if debug and i == 0:
                                print(f"DEBUG: Empty value for column {col_name}")
                            continue
                        
                        if debug and i == 0:
                            print(f"DEBUG: Original value for {col_name}: '{value}'")
                        
                        
                        if 'transformations' in col_config:
                            value = apply_transformations(value, col_config['transformations'], debug)
                            if debug and i == 0:
                                print(f"DEBUG: After column transformations: '{value}'")
                        
                        
                        if global_transformations:
                            
                            if isinstance(value, list):
                                new_value = []
                                for item in value:
                                    if isinstance(item, str) and item:
                                        
                                        transformed_item = apply_transformations(item, global_transformations, debug)
                                        if transformed_item and transformed_item != "":
                                            if isinstance(transformed_item, list):
                                                new_value.extend(transformed_item)
                                            else:
                                                new_value.append(transformed_item)
                                value = new_value
                            else:
                                value = apply_transformations(value, global_transformations, debug)
                            if debug and i == 0:
                                print(f"DEBUG: After global transformations: '{value}'")
                        
                        
                        if isinstance(value, list):
                            normalized_list = []
                            for item in value:
                                if isinstance(item, str) and item:
                                    normalized_item = normalize_string(item)
                                    if normalized_item and normalized_item not in normalized_list:
                                        normalized_list.append(normalized_item)
                            value = normalized_list
                        elif isinstance(value, str) and value:
                            value = normalize_string(value)
                        
                        
                        if (isinstance(value, list) and value) or (isinstance(value, str) and value):
                            processed_row['classes'][class_name][col_name] = value
            
            
            for parse_config in file_config['parse']:
                if parse_config['type'] == 'attribute':
                    attribute_name = parse_config['attribute']
                    class_to = parse_config['class-to']
                    class_from = parse_config['class-from']
                    columns_config = parse_config['columns']
                    
                    if debug and i == 0:
                        print(f"DEBUG: Processing attribute {attribute_name}: {class_to} -> {class_from} using columns {columns_config}")
                    
                    all_values = []
                    
                    
                    for column_config in columns_config:
                        if isinstance(column_config, dict) and 'column' in column_config:
                            column_name = column_config['column']
                            
                            transformations = column_config.get('transformations', [])
                        else:
                            column_name = column_config
                            transformations = []
                        
                        if column_name not in row:
                            if debug and i == 0:
                                print(f"DEBUG: Column {column_name} not found in row for attribute {attribute_name}")
                            continue
                        
                        value = row[column_name].strip()
                        if not value or value == 'NULL':
                            if debug and i == 0:
                                print(f"DEBUG: Empty value for column {column_name} in attribute {attribute_name}")
                            continue
                        
                        
                        if not transformations and class_from in all_data['class_definitions']:
                            if column_name in all_data['class_definitions'][class_from]:
                                transformations = all_data['class_definitions'][class_from][column_name]['transformations']
                        
                        
                        if transformations:
                            value = apply_transformations(value, transformations, debug)
                        
                        
                        if global_transformations:
                            if isinstance(value, list):
                                new_value = []
                                for item in value:
                                    if isinstance(item, str) and item:
                                        transformed_item = apply_transformations(item, global_transformations, debug)
                                        if transformed_item and transformed_item != "":
                                            if isinstance(transformed_item, list):
                                                new_value.extend(transformed_item)
                                            else:
                                                new_value.append(transformed_item)
                                value = new_value
                            else:
                                value = apply_transformations(value, global_transformations, debug)
                        
                        
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, str) and item:
                                    normalized_item = normalize_string(item)
                                    if normalized_item and normalized_item not in all_values:
                                        all_values.append(normalized_item)
                        elif isinstance(value, str) and value:
                            normalized_value = normalize_string(value)
                            if normalized_value not in all_values:
                                all_values.append(normalized_value)
                    
                    
                    if all_values:
                        processed_row['attributes'].append({
                            'name': attribute_name,
                            'class-to': class_to,
                            'class-from': class_from,
                            'values': all_values
                        })
                        
                        if debug and i == 0:
                            print(f"DEBUG: Added attribute {attribute_name} with values: {all_values}")
            
            all_data['rows'].append(processed_row)
        
        all_data['files_processed'].append(file_config['file'])
    
    return all_data