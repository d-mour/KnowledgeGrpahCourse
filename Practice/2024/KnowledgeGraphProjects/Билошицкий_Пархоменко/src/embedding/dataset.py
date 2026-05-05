import json
import pandas as pd
import os
from pathlib import Path

def load_json_data(directory, filename):
    """Load JSON data from a file."""
    file_path = os.path.join(directory, filename)
    with open(file_path, 'r') as f:
        return json.load(f)

def create_items_dataset(tools_data, swords_data, armor_data):
    """Create items dataset from tools, swords, and armor data."""
    items = []
    
    # Process tools
    for tool_name, tool_info in tools_data.items():
        item = {
            'Item_Name': tool_name,
            'Item_Type': get_tool_type(tool_name),
            'Material_Name': None,
            'Material_Count': None,
            'Durability': tool_info.get('durability'),
            'Attack_Damage': None,
            'Protection_Value': None
        }
        
        # Add crafting materials if available
        if 'crafting' in tool_info and 'grid' in tool_info['crafting']:
            materials = get_materials_from_grid(tool_info['crafting']['grid'])
            if materials:
                item['Material_Name'] = list(materials.keys())[0]  # Primary material
                item['Material_Count'] = materials[item['Material_Name']]
        
        items.append(item)
    
    # Process swords
    for sword_name, sword_info in swords_data.items():
        item = {
            'Item_Name': sword_name,
            'Item_Type': 'CombatTool',
            'Material_Name': None,
            'Material_Count': None,
            'Durability': sword_info.get('durability'),
            'Attack_Damage': sword_info.get('attack_damage'),
            'Protection_Value': None
        }
        
        if 'crafting' in sword_info and 'grid' in sword_info['crafting']:
            materials = get_materials_from_grid(sword_info['crafting']['grid'])
            if materials:
                item['Material_Name'] = list(materials.keys())[0]
                item['Material_Count'] = materials[item['Material_Name']]
        
        items.append(item)
    
    # Process armor
    for armor_name, armor_info in armor_data.items():
        item = {
            'Item_Name': armor_name,
            'Item_Type': 'Armor',
            'Material_Name': None,
            'Material_Count': None,
            'Durability': armor_info.get('durability'),
            'Attack_Damage': None,
            'Protection_Value': armor_info.get('protection')
        }
        
        if 'crafting' in armor_info and 'grid' in armor_info['crafting']:
            materials = get_materials_from_grid(armor_info['crafting']['grid'])
            if materials:
                item['Material_Name'] = list(materials.keys())[0]
                item['Material_Count'] = materials[item['Material_Name']]
        
        items.append(item)
    
    return pd.DataFrame(items)

def create_recipes_dataset(tools_data, swords_data, armor_data):
    """Create recipes dataset from tools, swords, and armor data."""
    recipes = []
    
    # Process all item types
    for item_data in [tools_data, swords_data, armor_data]:
        for item_name, item_info in item_data.items():
            if 'crafting' in item_info and 'grid' in item_info['crafting']:
                materials = get_materials_from_grid(item_info['crafting']['grid'])
                
                for material_name, count in materials.items():
                    recipe = {
                        'Recipe_Name': f"{item_name} Recipe",
                        'Item_Name': item_name,
                        'Material_Name': material_name,
                        'Material_Count': count
                    }
                    recipes.append(recipe)
    
    return pd.DataFrame(recipes)

def create_ores_dataset(ores_data):
    """Create ores dataset from ores data."""
    ores = []
    
    for ore_name, ore_info in ores_data.items():
        ore = {
            'Ore_Name': ore_name,
            'Abundance': ore_info.get('Abundance'),
            'Requires_Pickaxe': ore_info.get('Minimum pickaxe tier required')
        }
        ores.append(ore)
    
    return pd.DataFrame(ores)

def get_tool_type(tool_name):
    """Determine tool type based on name."""
    tool_name = tool_name.lower()
    if any(x in tool_name for x in ['pickaxe', 'axe']):
        return 'MiningTool'
    elif any(x in tool_name for x in ['hoe', 'shovel']):
        return 'FarmingTool'
    elif 'sword' in tool_name:
        return 'CombatTool'
    elif any(x in tool_name for x in ['fishing_rod', 'flint_and_steel', 'shears', 'brush', 'spyglass']):
        return 'SpecialTool'
    return 'Tool'

def get_materials_from_grid(grid):
    """Extract materials and their counts from crafting grid."""
    materials = {}
    for row in grid:
        for item in row:
            if item and isinstance(item, dict) and 'item' in item:
                material = item['item']
                materials[material] = materials.get(material, 0) + 1
    return materials

def save_datasets(output_dir):
    """Save all datasets to CSV and JSON formats."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Load source data
    tools_data = load_json_data('../../data/processed', 'tool_recipes.json')
    swords_data = load_json_data('../../data/processed', 'sword_recipes.json')
    armor_data = load_json_data('../../data/processed', 'armor_data.json')
    ores_data = load_json_data('../../data/processed', 'ore_data.json')
    
    # Create datasets
    items_df = create_items_dataset(tools_data, swords_data, armor_data)
    recipes_df = create_recipes_dataset(tools_data, swords_data, armor_data)
    ores_df = create_ores_dataset(ores_data)
    
    # Save as CSV
    items_df.to_csv(f"{output_dir}/items.csv", index=False)
    recipes_df.to_csv(f"{output_dir}/recipes.csv", index=False)
    ores_df.to_csv(f"{output_dir}/ores.csv", index=False)
    
    # Save as JSON
    items_df.to_json(f"{output_dir}/items.json", orient='records', indent=2)
    recipes_df.to_json(f"{output_dir}/recipes.json", orient='records', indent=2)
    ores_df.to_json(f"{output_dir}/ores.json", orient='records', indent=2)
    
    print(f"Datasets saved to {output_dir}")
    return items_df, recipes_df, ores_df

if __name__ == "__main__":
    output_directory = "data/datasets"
    items_df, recipes_df, ores_df = save_datasets(output_directory)
    
    # Print sample of each dataset
    print("\nItems Dataset Sample:")
    print(items_df.head())
    print("\nRecipes Dataset Sample:")
    print(recipes_df.head())
    print("\nOres Dataset Sample:")
    print(ores_df.head())