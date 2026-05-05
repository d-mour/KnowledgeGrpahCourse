import yaml
from pathlib import Path
from typing import Dict, Any, List

def load_config(config_path: str) -> Dict[str, Any]:
    print(f"Reading config from {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    print(f"Raw config data type: {type(config_data)}")
    
    
    if not isinstance(config_data, list):
        raise ValueError(f"Config should be a list, got {type(config_data)}")
    
    processed_config = {
        'global_transformations': [],
        'hierarchy': [],
        'files': []
    }
    
    for i, item in enumerate(config_data):
        if not isinstance(item, dict):
            print(f"Warning: Skipping non-dict item at index {i}: {item}")
            continue
            
        if 'all' in item:
            print("Found global transformations")
            if isinstance(item['all'], list) and len(item['all']) > 0:
                all_item = item['all'][0]
                if 'transformations' in all_item:
                    processed_config['global_transformations'] = all_item['transformations']
        elif 'hierarchy' in item:
            print("Found class hierarchy")
            processed_config['hierarchy'] = item['hierarchy']
        elif 'file' in item:
            print(f"Found file config: {item['file']}")
            
            
            file_config = {'file': item['file'], 'parse': []}
            
            for parse_item in item.get('parse', []):
                if 'class' in parse_item:
                    
                    file_config['parse'].append({
                        'type': 'class',
                        'class': parse_item['class'],
                        'columns': parse_item['columns']
                    })
                elif 'attribute' in parse_item:
                    
                    attribute_config = {
                        'type': 'attribute',
                        'attribute': parse_item['attribute'],
                        'class-to': parse_item['class-to'],
                        'class-from': parse_item['class-from']
                    }
                    
                    
                    if 'column' in parse_item:
                        
                        attribute_config['columns'] = [{'column': parse_item['column']}]
                    elif 'columns' in parse_item:
                        
                        attribute_config['columns'] = []
                        for col_item in parse_item['columns']:
                            if isinstance(col_item, dict):
                                
                                attribute_config['columns'].append(col_item)
                            else:
                                
                                attribute_config['columns'].append({'column': col_item})
                    else:
                        print(f"Warning: Attribute {parse_item['attribute']} has neither 'column' nor 'columns'")
                        continue
                    
                    file_config['parse'].append(attribute_config)
            
            processed_config['files'].append(file_config)
    
    print(f"Processed config: {processed_config}")
    return processed_config