import urllib.parse
import re
from typing import Any, List, Dict

def normalize_string(s: str) -> str:
    """Нормализует строку для использования в URI"""
    if not isinstance(s, str):
        s = str(s)
    
    
    s = s.lower()
    
    
    s = s.replace('damage', 'dmg')
    s = s.replace('recarge', 'recharge')  
    s = s.replace('recharge', 'recharge')  
    
    
    s = s.replace(' ', '_')
    s = s.replace(',', '_')
    s = s.replace('/', '_')
    s = s.replace(':', '')
    s = s.replace('★', '')
    s = s.replace('"', '')
    s = s.replace("'", '')
    s = s.replace('(', '')
    s = s.replace(')', '')
    s = s.replace('%', '_percent')
    s = s.replace('[', '')
    s = s.replace(']', '')
    
    
    while '__' in s:
        s = s.replace('__', '_')
    s = s.strip('_')
    
    
    return urllib.parse.quote(s, safe='_')

def apply_transformations(value: str, transformations: List[Dict], debug: bool = False) -> Any:
    """Применяет трансформации к значению"""
    if not isinstance(value, str):
        value = str(value)
        
    result = value
    
    if debug:
        print(f"  Applying transformations to: '{result}'")
    
    for i, transform in enumerate(transformations):
        if debug:
            print(f"    Transformation {i}: {transform}")
            
        
        if 'replace' in transform:
            
            if transform['replace'] is not None:
                from_val = transform['replace']['from']
                to_val = transform['replace']['to']
            else:
                
                from_val = transform['from']
                to_val = transform['to']
                
            if debug:
                print(f"      Replace: '{from_val}' -> '{to_val}'")
            
            
            if isinstance(result, list):
                new_result = []
                for item in result:
                    if isinstance(item, str):
                        new_result.append(item.replace(from_val, to_val))
                result = new_result
            else:
                result = result.replace(from_val, to_val)
            
            if debug:
                print(f"      Result after replace: {result}")
                
        
        elif 'split' in transform:
            
            if transform['split'] is not None:
                delimiter = transform['split']['by']
            else:
                
                delimiter = transform['by']
                
            if debug:
                print(f"      Split by: '{delimiter}'")
                
            
            if isinstance(result, list):
                new_result = []
                for item in result:
                    if isinstance(item, str):
                        
                        split_items = [i.strip() for i in item.split(delimiter) if i.strip()]
                        new_result.extend(split_items)
                result = new_result
            else:
                
                result = [i.strip() for i in result.split(delimiter) if i.strip()]
                
            if debug:
                print(f"      Result after split: {result}")
                
        
        elif 'truncate' in transform:
            
            if transform['truncate'] is not None:
                truncate_by = transform['truncate']['by']
            else:
                
                truncate_by = transform['by']
                
            if debug:
                print(f"      Truncate by: '{truncate_by}'")
            
            
            if isinstance(result, list):
                new_result = []
                for item in result:
                    if isinstance(item, str) and truncate_by not in item:
                        new_result.append(item)
                result = new_result
            else:
                
                if truncate_by in result:
                    result = ""
                
            if debug:
                print(f"      Result after truncate: {result}")
    
    if debug:
        print(f"  Result after transformations (before normalize): {result}")
    
    return result