def get_armor_queries():
    return {
        "Find complete armor sets and their protection values": """
        SELECT DISTINCT ?set_name ?piece_name ?protection ?durability
        WHERE {
            ?armor_set a mc:ArmorSet ;
                      rdfs:label ?set_name .
            ?piece mc:isPartOfArmorSet ?armor_set ;
                   rdfs:label ?piece_name ;
                   mc:hasProtectionValue ?protection ;
                   mc:hasBaseDurability ?durability .
        }
        ORDER BY ?set_name DESC(?protection)
        """,
        "Find armor recipes and their material requirements": """
        SELECT DISTINCT ?armor_name ?material_name ?count
        WHERE {
            ?armor a mc:Armor ;
                   rdfs:label ?armor_name ;
                   mc:hasRecipe ?recipe .
            ?recipe mc:usesMaterial ?material ;
                    mc:materialCount ?count .
            ?material rdfs:label ?material_name .
        }
        ORDER BY ?armor_name ?material_name
        """,
    }


def get_tool_queries():
    return {
        "List all tools with their durability and crafting materials": """
        SELECT DISTINCT ?tool_name ?durability ?material_name ?count
        WHERE {
            ?tool a mc:Tool ;
                  rdfs:label ?tool_name ;
                  mc:hasDurability ?durability ;
                  mc:hasRecipe ?recipe .
            ?recipe mc:usesMaterial ?material ;
                    mc:materialCount ?count .
            ?material rdfs:label ?material_name .
        }
        ORDER BY ?tool_name
        """,
        "List all swords with their combat stats": """
        SELECT DISTINCT ?sword_name ?durability ?attack_damage ?attack_speed ?dps
        WHERE {
            ?sword a mc:CombatTool ;
                   rdfs:label ?sword_name ;
                   mc:hasDurability ?durability .
            OPTIONAL { ?sword mc:hasAttackDamage ?attack_damage }
            OPTIONAL { ?sword mc:hasAttackSpeed ?attack_speed }
            OPTIONAL { ?sword mc:hasDPS ?dps }
            FILTER(CONTAINS(LCASE(?sword_name), "sword"))
        }
        ORDER BY ?sword_name
        """,
    }


def get_mining_capability_query(tool_name="Diamond Pickaxe", ore_name="Iron_Ore"):
    query = f"""
    SELECT (IF(?tool_value >= ?req_value, "Yes", "No") as ?can_mine)
    WHERE {{
        ?ore a mc:Ore ;
             rdfs:label "{ore_name}" ;
             mc:requiresPickaxe ?required_tool .
        ?required_tool rdfs:label ?required_tier .
        
        BIND("{tool_name}" AS ?tool_name)
        
        VALUES (?pickaxe_name ?tool_value) {{
            ("Wooden Pickaxe"    1)
            ("Stone Pickaxe"     2)
            ("Iron Pickaxe"      3)
            ("Golden Pickaxe"    2)
            ("Diamond Pickaxe"   4)
        }}
        
        VALUES (?req_pickaxe ?req_value) {{
            ("Wooden Pickaxe"    1)
            ("Stone Pickaxe"     2)
            ("Iron Pickaxe"      3)
            ("Diamond Pickaxe"   4)
        }}
        
        FILTER(?pickaxe_name = ?tool_name)
        FILTER(?req_pickaxe = ?required_tier)
    }}
    """
    return {f"Can {tool_name} mine {ore_name}?": query}


def get_ore_mining_tools_query(ore_name="Diamond_Ore"):
    return {
        f"2. What tools can mine {ore_name}?": f"""
        SELECT DISTINCT ?tool_name
        WHERE {{
            ?ore a mc:Ore ;
                 rdfs:label "{ore_name}" ;
                 mc:requiresPickaxe ?required_tool .
            ?required_tool rdfs:label ?required_tier .
            
            VALUES (?pickaxe_name ?tool_value) {{
                ("Wooden Pickaxe"    1)
                ("Stone Pickaxe"     2)
                ("Iron Pickaxe"      3)
                ("Golden Pickaxe"    2)
                ("Diamond Pickaxe"   4)
                ("Netherite Pickaxe" 5)
            }}
            
            VALUES (?req_pickaxe ?req_value) {{
                ("Wooden Pickaxe"    1)
                ("Stone Pickaxe"     2)
                ("Iron Pickaxe"      3)
                ("Diamond Pickaxe"   4)
                ("Netherite Pickaxe" 5)
            }}
            
            FILTER(?req_pickaxe = ?required_tier)
            FILTER(?tool_value >= ?req_value)
            BIND(?pickaxe_name AS ?tool_name)
        }}
        ORDER BY ?tool_name
        """
    }


def get_item_recipe_query(item_name="Diamond Boots"):
    return {
        f"3. What is the recipe for {item_name}?": f"""
        SELECT ?grid
        WHERE {{
            ?item rdfs:label "{item_name}" .
            {{
                ?item mc:hasRecipe ?recipe .
                ?recipe mc:recipeGrid ?grid .
            }} UNION {{
                ?item mc:hasArmorRecipe ?recipe .
                ?recipe mc:recipeGrid ?grid .
            }}
        }}
        LIMIT 1
        """
    }


def get_item_durability_query(item_name="Diamond Pickaxe"):
    return {
        f"4. What is the durability of {item_name}?": f"""
        SELECT ?durability
        WHERE {{
            ?item rdfs:label "{item_name}" ;
                  mc:hasDurability ?durability .
        }}
        """
    }


def get_sword_damage_query(sword_name="Diamond Sword"):
    return {
        f"5. What is the attack damage of {sword_name}?": f"""
        SELECT ?attack_damage
        WHERE {{
            ?sword a mc:CombatTool ;
                   rdfs:label "{sword_name}" ;
                   mc:hasAttackDamage ?attack_damage .
        }}
        """
    }


def get_crafting_requirement_query(
    item_name="Diamond Sword", material_name="Diamond"
):
    material_name = material_name.replace(" ", "_")
    material_count_property = f"mc:{material_name}_Count"
    return {
        f"6. Is {material_name} required for crafting {item_name}?": f"""
        SELECT (COUNT(?recipe) > 0 as ?is_required)
        WHERE {{
            ?item rdfs:label "{item_name}" .
            {{
                ?item mc:hasRecipe ?recipe .
                ?recipe {material_count_property} ?count .
            }} UNION {{
                ?item mc:hasArmorRecipe ?recipe .
                ?recipe {material_count_property} ?count .
            }}
            FILTER(?count > 0)
        }}
        """
    }


def get_crafting_yield_query(item_name="Iron Pickaxe", material_name="Iron Ingot"):
    material_name = material_name.replace(" ", "_")
    return {
        f"7. How many {material_name} are needed to craft {item_name}?": f"""
        SELECT ?count
        WHERE {{
            ?item rdfs:label "{item_name}" ;
                  mc:hasRecipe ?recipe .
            ?recipe mc:usesMaterial ?material .
            ?material rdfs:label "{material_name}" .
            ?recipe mc:{material_name}_Count ?count .
        }}
        """
    }


def get_armor_set_pieces_query(set_name="Diamond Set"):
    return {
        f"8. What items are part of {set_name}?": f"""
        SELECT ?piece_name
        WHERE {{
            ?armor_set a mc:ArmorSet ;
                      rdfs:label "{set_name}" .
            ?piece mc:isPartOfArmorSet ?armor_set ;
                   rdfs:label ?piece_name .
        }}
        ORDER BY ?piece_name
        """
    }


def get_sword_dps_query(sword_name="Diamond Sword"):
    return {
        f"9. What is the DPS of {sword_name}?": f"""
        SELECT ?dps
        WHERE {{
            ?sword a mc:CombatTool ;
                   rdfs:label "{sword_name}" ;
                   mc:hasDPS ?dps .
        }}
        """
    }


def get_items_crafted_from(material_x="Iron Ingot", material_y="Stick"):
    material_x = material_x.replace(" ", "_")
    material_y = material_y.replace(" ", "_")
    material_x_count = f"mc:{material_x}_Count"
    material_y_count = f"mc:{material_y}_Count"
    return {
        f"10. What items can be crafted from {material_x} and {material_y}?": f"""
        SELECT DISTINCT ?item_name ?{material_x}_count ?{material_y}_count
        WHERE {{
            ?item rdfs:label ?item_name .
            ?item mc:hasRecipe|mc:hasArmorRecipe ?recipe .
            ?recipe {material_x_count} ?{material_x}_count ;
                   {material_y_count} ?{material_y}_count .
            ?material_x rdfs:label "{material_x}" .
            ?material_y rdfs:label "{material_y}" .
        }}
        ORDER BY ?item_name
        """
    }


def get_ore_height_range_query(ore_name="Emerald_Ore"):
    return {
        f"11. On which layer can {ore_name} be found?": f"""
        SELECT ?layer_name
        WHERE {{
            ?ore a mc:Ore ;
                 rdfs:label "{ore_name}" ;
                 mc:foundInLayer ?layer .
            ?layer rdfs:label ?layer_name .
        }}
        """
    }


def get_competence_queries():
    queries = {}
    queries.update(get_mining_capability_query())
    queries.update(get_ore_mining_tools_query())
    queries.update(get_item_recipe_query())
    queries.update(get_item_durability_query())
    queries.update(get_sword_damage_query())
    queries.update(get_crafting_requirement_query())
    queries.update(get_crafting_yield_query())
    queries.update(get_armor_set_pieces_query())
    queries.update(get_sword_dps_query())
    queries.update(get_items_crafted_from())
    queries.update(get_ore_height_range_query())
    return queries
