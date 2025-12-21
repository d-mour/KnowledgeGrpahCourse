from rdflib import OWL, Graph, Literal, RDF, RDFS, Namespace
from rdflib.namespace import XSD
import json
import os
from src.parsers import PROCESSED_DATA_DIR, DATA_DIR
from src.utils.file_utils import load_json_data
from src.ontology.minecraft_queries import (
    get_competence_queries,
)

# Create namespaces
MC = Namespace("http://minecraft.example.org/")
TOOL = Namespace("http://minecraft.example.org/tool/")
ORE = Namespace("http://minecraft.example.org/ore/")
MATERIAL = Namespace("http://minecraft.example.org/material/")
BIOME = Namespace("http://minecraft.example.org/biome/")
LAYER = Namespace("http://minecraft.example.org/layer/")
RECIPE = Namespace("http://minecraft.example.org/recipe/")
ARMOR = Namespace("http://minecraft.example.org/armor/")


def create_minecraft_ontology():
    g = Graph()

    # Bind namespaces
    g.bind("mc", MC)
    g.bind("tool", TOOL)
    g.bind("ore", ORE)
    g.bind("material", MATERIAL)
    g.bind("biome", BIOME)
    g.bind("layer", LAYER)
    g.bind("recipe", RECIPE)
    g.bind("armor", ARMOR)

    # Define main classes
    g.add((MC.Tool, RDF.type, RDFS.Class))
    g.add((MC.Ore, RDF.type, RDFS.Class))
    g.add((MC.Material, RDF.type, RDFS.Class))
    g.add((MC.Biome, RDF.type, RDFS.Class))
    g.add((MC.Layer, RDF.type, RDFS.Class))
    g.add((MC.Recipe, RDF.type, RDFS.Class))
    g.add((MC.Armor, RDF.type, RDFS.Class))

    # Define subclasses
    g.add((MC.MiningTool, RDFS.subClassOf, MC.Tool))
    g.add((MC.CombatTool, RDFS.subClassOf, MC.Tool))
    g.add((MC.FarmingTool, RDFS.subClassOf, MC.Tool))
    g.add((MC.SpecialTool, RDFS.subClassOf, MC.Tool))

    # Define recipe-related properties
    g.add((MC.hasRecipe, RDF.type, OWL.ObjectProperty))
    g.add((MC.hasRecipe, RDFS.domain, OWL.Thing))
    g.add((MC.hasRecipe, RDFS.range, MC.Recipe))

    g.add((MC.usesMaterial, RDF.type, OWL.ObjectProperty))
    g.add((MC.usesMaterial, RDFS.domain, MC.Recipe))
    g.add((MC.usesMaterial, RDFS.range, MC.Material))

    g.add((MC.materialCount, RDF.type, OWL.DatatypeProperty))
    g.add((MC.materialCount, RDFS.domain, MC.Recipe))
    g.add((MC.materialCount, RDFS.range, XSD.integer))

    # For Diamond Sword recipe
    sword_uri = TOOL["Diamond_Sword"]
    sword_recipe_uri = RECIPE["Diamond_Sword_Recipe"]
    diamond_uri = MATERIAL["Diamond"]
    stick_uri = MATERIAL["Stick"]

    # Add recipe relationships
    g.add((sword_uri, MC.hasRecipe, sword_recipe_uri))
    g.add((sword_recipe_uri, RDF.type, MC.Recipe))
    g.add((sword_recipe_uri, MC.usesMaterial, diamond_uri))
    g.add((sword_recipe_uri, MC.usesMaterial, stick_uri))
    g.add(
        (sword_recipe_uri, MC.materialCount, Literal(2, datatype=XSD.integer))
    )  # Diamond count
    g.add(
        (sword_recipe_uri, MC.materialCount, Literal(1, datatype=XSD.integer))
    )  # Stick count

    # For Iron Pickaxe recipe
    pickaxe_uri = TOOL["Iron_Pickaxe"]
    pickaxe_recipe_uri = RECIPE["Iron_Pickaxe_Recipe"]
    iron_uri = MATERIAL["Iron_Ingot"]
    stick_uri = MATERIAL["Stick"]

    # Add recipe relationships
    g.add((pickaxe_uri, MC.hasRecipe, pickaxe_recipe_uri))
    g.add((pickaxe_recipe_uri, RDF.type, MC.Recipe))
    g.add((pickaxe_recipe_uri, MC.usesMaterial, iron_uri))
    g.add((pickaxe_recipe_uri, MC.usesMaterial, stick_uri))

    # Add specific material count properties
    iron_count_property = MC["Iron_Ingot_Count"]
    stick_count_property = MC["Stick_Count"]

    g.add((iron_count_property, RDF.type, OWL.DatatypeProperty))
    g.add((stick_count_property, RDF.type, OWL.DatatypeProperty))

    g.add((pickaxe_recipe_uri, iron_count_property, Literal(3, datatype=XSD.integer)))
    g.add((pickaxe_recipe_uri, stick_count_property, Literal(2, datatype=XSD.integer)))

    # Add labels
    g.add((pickaxe_uri, RDFS.label, Literal("Iron Pickaxe")))
    g.add((iron_uri, RDFS.label, Literal("Iron Ingot")))
    g.add((stick_uri, RDFS.label, Literal("Stick")))

    # Load ore data from JSON
    ores_data = load_json_data(PROCESSED_DATA_DIR, "ore_data.json")

    # Add ore information
    for ore_name, ore_data in ores_data.items():
        ore_name = ore_name.replace(" ", "_") + "_Ore"
        ore_uri = ORE[ore_name]
        g.add((ore_uri, RDF.type, MC.Ore))
        g.add((ore_uri, RDFS.label, Literal(ore_name)))

        # Add pickaxe requirement
        if "Minimum pickaxe tier required" in ore_data:
            pickaxe_type = ore_data["Minimum pickaxe tier required"]
            g.add((ore_uri, MC.requiresPickaxe, TOOL[f"{pickaxe_type}_Pickaxe"]))

        # Add abundance
        if "Abundance" in ore_data:
            g.add((ore_uri, MC.hasAbundance, Literal(ore_data["Abundance"])))

        # Add biome information
        if "Found in biome" in ore_data:
            biome_info = ore_data["Found in biome"]
            if biome_info["type"] == "specific":
                for biome in biome_info["biomes"]:
                    biome_uri = BIOME[biome.replace(" ", "_")]
                    g.add((biome_uri, RDF.type, MC.Biome))
                    g.add((ore_uri, MC.foundInBiome, biome_uri))
            else:
                g.add((ore_uri, MC.isUniversal, Literal(True)))

        layer_uri = LAYER[ore_data["Total range"].replace(" ", "_")]
        g.add((layer_uri, RDF.type, MC.Layer))
        g.add((layer_uri, RDFS.label, Literal(ore_data["Total range"])))
        g.add((ore_uri, MC.foundInLayer, layer_uri))

    # Load tool data from JSON
    tools_data = load_json_data(PROCESSED_DATA_DIR, "tool_recipes.json")

    # Add tool and recipe information
    for tool_name, tool_info in tools_data.items():
        # Normalize tool name by removing spaces and converting to title case
        normalized_tool_name = tool_name.replace(" ", "_").title()
        tool_uri = TOOL[normalized_tool_name]
        g.add((tool_uri, RDF.type, MC.Tool))
        g.add((tool_uri, RDFS.label, Literal(tool_name)))

        if "durability" in tool_info:
            g.add(
                (
                    tool_uri,
                    MC.hasDurability,
                    Literal(tool_info["durability"], datatype=XSD.integer),
                )
            )

        # Add recipe information
        if "crafting" in tool_info and "grid" in tool_info["crafting"]:
            recipe_uri = MC[tool_name.replace(" ", "_") + "_Recipe"]
            g.add((recipe_uri, RDF.type, MC.Recipe))
            g.add((tool_uri, MC.hasRecipe, recipe_uri))
            g.add((recipe_uri, MC.isRecipeFor, tool_uri))

            # Simplify grid to just item names
            simplified_grid = []
            material_counts = {}

            for row in tool_info["crafting"]["grid"]:
                grid_row = []
                for item in row:
                    if item and "item" in item:
                        material = item["item"]
                        grid_row.append(material)
                        material_counts[material] = material_counts.get(material, 0) + 1
                    else:
                        grid_row.append(None)
                simplified_grid.append(grid_row)

            # Store the simplified grid as a JSON string
            grid_json = json.dumps(simplified_grid)
            g.add((recipe_uri, MC.recipeGrid, Literal(grid_json)))

            # Add material relationships to recipe
            for material, count in material_counts.items():
                material_uri = MATERIAL[material.replace(" ", "_")]
                g.add((material_uri, RDF.type, MC.Material))
                g.add((material_uri, RDFS.label, Literal(material)))

                # Create a specific property for each material count
                material_count_property = MC[f"has{material.replace(' ', '')}Count"]
                g.add((material_count_property, RDF.type, OWL.DatatypeProperty))
                g.add((material_count_property, RDFS.domain, MC.Recipe))
                g.add((material_count_property, RDFS.range, XSD.integer))
                g.add(
                    (
                        recipe_uri,
                        material_count_property,
                        Literal(count, datatype=XSD.integer),
                    )
                )

            # Find primary material (most used in recipe)
            if material_counts:
                primary_material = max(material_counts.items(), key=lambda x: x[1])[0]
                primary_material_uri = MATERIAL[primary_material.replace(" ", "_")]
                g.add((recipe_uri, MC.primaryMaterial, primary_material_uri))

    # Load armor data from JSON
    armor_data = load_json_data(PROCESSED_DATA_DIR, "armor_data.json")

    # Add armor information
    for armor_name, armor_info in armor_data.items():
        armor_uri = ARMOR[armor_name.replace(" ", "_")]
        g.add((armor_uri, RDF.type, MC.Armor))
        g.add((armor_uri, RDFS.label, Literal(armor_name)))

        # Add recipe information if available
        if "crafting" in armor_info and "grid" in armor_info["crafting"]:
            recipe_uri = RECIPE[armor_name.replace(" ", "_") + "_Recipe"]
            g.add((recipe_uri, RDF.type, MC.Recipe))
            g.add((armor_uri, MC.hasRecipe, recipe_uri))
            g.add((recipe_uri, MC.isRecipeFor, armor_uri))

            # Process crafting grid
            simplified_grid = []
            material_counts = {}

            for row in armor_info["crafting"]["grid"]:
                grid_row = []
                for item in row:
                    if item and "item" in item:
                        material = item["item"]
                        grid_row.append(material)
                        material_counts[material] = material_counts.get(material, 0) + 1
                    else:
                        grid_row.append(None)
                simplified_grid.append(grid_row)

            # Store the simplified grid as a JSON string
            grid_json = json.dumps(simplified_grid)
            g.add((recipe_uri, MC.recipeGrid, Literal(grid_json)))

            # Add material relationships to recipe
            for material, count in material_counts.items():
                material_uri = MATERIAL[material.replace(" ", "_")]
                g.add((material_uri, RDF.type, MC.Material))
                g.add((material_uri, RDFS.label, Literal(material)))

                # Create a specific property for each material count
                material_count_property = MC[f"{material.replace(' ', '_')}_Count"]
                g.add((material_count_property, RDF.type, OWL.DatatypeProperty))
                g.add((material_count_property, RDFS.domain, MC.Recipe))
                g.add((material_count_property, RDFS.range, XSD.integer))
                g.add(
                    (
                        recipe_uri,
                        material_count_property,
                        Literal(count, datatype=XSD.integer),
                    )
                )

                # Find primary material (most used in recipe)
                if material_counts:
                    primary_material = max(material_counts.items(), key=lambda x: x[1])[
                        0
                    ]
                    primary_material_uri = MATERIAL[primary_material.replace(" ", "_")]
                    g.add((recipe_uri, MC.primaryMaterial, primary_material_uri))

        # Determine material and type
        material_types = {
            "leather": "Leather",
            "golden": "Gold",
            "chainmail": "Chainmail",
            "iron": "Iron",
            "diamond": "Diamond",
        }

        armor_slots = ["helmet", "chestplate", "leggings", "boots"]

        # Find material and slot
        found_material = None
        for mat_key, mat_name in material_types.items():
            if mat_key in armor_name.lower():
                found_material = mat_name
                material_uri = MATERIAL[mat_name]
                g.add((material_uri, RDF.type, MC.Material))
                g.add((material_uri, RDFS.label, Literal(mat_name)))
                break

        # Add armor set
        if found_material:
            armor_set_uri = ARMOR[f"{found_material}_Set"]
            g.add((armor_set_uri, RDF.type, MC.ArmorSet))
            g.add((armor_set_uri, RDFS.label, Literal(f"{found_material} Set")))
            g.add((armor_uri, MC.isPartOfArmorSet, armor_set_uri))

            # Connect armor set to its pieces
            if any(["helmet" in armor_name.lower(), "cap" in armor_name.lower()]):
                g.add((armor_set_uri, MC.hasHelmet, armor_uri))
            elif any(
                ["chestplate" in armor_name.lower(), "tunic" in armor_name.lower()]
            ):
                g.add((armor_set_uri, MC.hasChestplate, armor_uri))
            elif any(["leggings" in armor_name.lower(), "pants" in armor_name.lower()]):
                g.add((armor_set_uri, MC.hasLeggings, armor_uri))
            elif "boots" in armor_name.lower():
                g.add((armor_set_uri, MC.hasBoots, armor_uri))

            # Add material tier
            material_tiers = {
                "Leather": 1,
                "Gold": 2,
                "Chainmail": 3,
                "Iron": 4,
                "Diamond": 5,
            }
            g.add(
                (
                    material_uri,
                    MC.hasMaterialTier,
                    Literal(material_tiers[found_material], datatype=XSD.integer),
                )
            )

            # Find slot and add protection/durability
            for slot in armor_slots:
                if slot in armor_name.lower():
                    g.add(
                        (
                            armor_uri,
                            MC.hasProtectionValue,
                            Literal(
                                armor_info["armor_points"],
                                datatype=XSD.integer,
                            ),
                        )
                    )
                    g.add(
                        (
                            armor_uri,
                            MC.hasBaseDurability,
                            Literal(armor_info["durability"], datatype=XSD.integer),
                        )
                    )
                    break

    # Load sword data from JSON
    sword_data = load_json_data(PROCESSED_DATA_DIR, "sword_recipes.json")

    # Add sword information
    for sword_name, sword_info in sword_data.items():
        sword_uri = TOOL[sword_name.replace(" ", "_")]
        g.add((sword_uri, RDF.type, MC.Tool))
        g.add((sword_uri, RDF.type, MC.CombatTool))  # Add sword as combat tool
        g.add((sword_uri, RDFS.label, Literal(sword_name)))

        # Add sword stats
        if "durability" in sword_info:
            g.add(
                (
                    sword_uri,
                    MC.hasDurability,
                    Literal(int(sword_info["durability"]), datatype=XSD.integer),
                )
            )

        if "attack_damage" in sword_info:
            g.add(
                (
                    sword_uri,
                    MC.hasAttackDamage,
                    Literal(float(sword_info["attack_damage"]), datatype=XSD.float),
                )
            )

        if "attack_speed" in sword_info:
            g.add(
                (
                    sword_uri,
                    MC.hasAttackSpeed,
                    Literal(float(sword_info["attack_speed"]), datatype=XSD.float),
                )
            )

        if "dps" in sword_info:
            g.add(
                (
                    sword_uri,
                    MC.hasDPS,
                    Literal(float(sword_info["dps"]), datatype=XSD.float),
                )
            )

        # Add recipe information
        if "crafting" in sword_info and "grid" in sword_info["crafting"]:
            recipe_uri = RECIPE[sword_name.replace(" ", "_") + "_Recipe"]
            g.add((recipe_uri, RDF.type, MC.Recipe))
            g.add((sword_uri, MC.hasRecipe, recipe_uri))
            g.add((recipe_uri, MC.isRecipeFor, sword_uri))

            # Process crafting grid
            simplified_grid = []
            material_counts = {}

            for row in sword_info["crafting"]["grid"]:
                grid_row = []
                for item in row:
                    if item and isinstance(item, dict) and "item" in item:
                        material = item["item"]
                        grid_row.append(material)
                        material_counts[material] = material_counts.get(material, 0) + 1
                    else:
                        grid_row.append(None)
                simplified_grid.append(grid_row)

            # Store the simplified grid as a JSON string
            grid_json = json.dumps(simplified_grid)
            g.add((recipe_uri, MC.recipeGrid, Literal(grid_json)))

            # Add material relationships to recipe
            for material, count in material_counts.items():
                material_uri = MATERIAL[material.replace(" ", "_")]
                g.add((material_uri, RDF.type, MC.Material))
                g.add((material_uri, RDFS.label, Literal(material)))

                # Create a specific property for each material count
                material_count_property = MC[f"{material.replace(' ', '_')}_Count"]
                g.add((material_count_property, RDF.type, OWL.DatatypeProperty))
                g.add((material_count_property, RDFS.domain, MC.Recipe))
                g.add((material_count_property, RDFS.range, XSD.integer))
                g.add(
                    (
                        recipe_uri,
                        material_count_property,
                        Literal(count, datatype=XSD.integer),
                    )
                )

                # Find primary material (most used in recipe)
                if material_counts:
                    primary_material = max(material_counts.items(), key=lambda x: x[1])[
                        0
                    ]
                    primary_material_uri = MATERIAL[primary_material.replace(" ", "_")]
                    g.add((recipe_uri, MC.primaryMaterial, primary_material_uri))

    # Add tool classifications
    farming_tools = ["Hoe", "Shovel"]
    mining_tools = ["Pickaxe", "Axe"]
    special_tools = ["Fishing_Rod", "Flint_and_Steel", "Shears", "Brush", "Spyglass"]

    # Add material prefixes for tools
    material_prefixes = ["Wooden", "Stone", "Iron", "Golden", "Diamond"]

    # Create and classify all tool variants
    for material in material_prefixes:
        # Add farming tools
        for tool in farming_tools:
            tool_name = f"{material}_{tool}"
            tool_uri = TOOL[tool_name]
            g.add((tool_uri, RDF.type, MC.Tool))
            g.add((tool_uri, RDF.type, MC.FarmingTool))
            g.add((tool_uri, RDFS.label, Literal(f"{material} {tool}")))

        # Add mining tools
        for tool in mining_tools:
            tool_name = f"{material}_{tool}"
            tool_uri = TOOL[tool_name]
            g.add((tool_uri, RDF.type, MC.Tool))
            g.add((tool_uri, RDF.type, MC.MiningTool))
            g.add((tool_uri, RDFS.label, Literal(f"{material} {tool}")))

    # Add special tools
    for tool in special_tools:
        tool_uri = TOOL[tool]
        g.add((tool_uri, RDF.type, MC.Tool))
        g.add((tool_uri, RDF.type, MC.SpecialTool))
        g.add((tool_uri, RDFS.label, Literal(tool.replace("_", " "))))

    # For Diamond crafting uses
    for item in [
        "Sword",
        "Pickaxe",
        "Axe",
        "Shovel",
        "Helmet",
        "Chestplate",
        "Leggings",
        "Boots",
    ]:
        item_uri = (
            TOOL[f"Diamond_{item}"]
            if item in ["Sword", "Pickaxe", "Axe", "Shovel"]
            else ARMOR[f"Diamond_{item}"]
        )
        g.add((diamond_uri, MC.isUsedIn, item_uri))
        g.add((item_uri, MC.usesMaterial, diamond_uri))

    return g, {}


def save_ontology(g, format="xml", filename="minecraft.owl"):
    """Save the ontology to the data directory."""
    output_path = os.path.join(DATA_DIR, filename)
    g.serialize(destination=output_path, format=format)
    print(f"Saved ontology to {output_path}")


def execute_query(g, description, query):
    print(f"\n{'='*80}")
    print(f"Query: {description}")
    print("=" * 80)

    results = g.query(query)
    columns = results.vars

    # Calculate column widths
    widths = {col: len(str(col)) for col in columns}
    for row in results:
        for col, value in zip(columns, row):
            widths[col] = max(widths[col], len(str(value)))

    # Print header
    header = " | ".join(f"{col:^{widths[col]}}" for col in columns)
    print("\n" + header)
    print("-" * len(header))

    # Print rows
    for row in results:
        formatted_values = []
        for col, value in zip(columns, row):
            formatted_values.append(f"{str(value):^{widths[col]}}")
        print(" | ".join(formatted_values))

    print(f"\nTotal results: {len(list(results))}\n")


def main():
    # Create and save the ontology
    g, _ = create_minecraft_ontology()
    save_ontology(g)

    print("\nMinecraft Ontology Analysis")
    print("=" * 80)

    # Print ontology statistics
    print(f"\nTotal triples: {len(g)}")
    print(f"Total classes: {len(list(g.subjects(RDF.type, RDFS.Class)))}")

    object_properties = len(list(g.subjects(RDF.type, OWL.ObjectProperty)))
    datatype_properties = len(list(g.subjects(RDF.type, OWL.DatatypeProperty)))
    print(f"Total properties: {object_properties + datatype_properties}")

    # Combine all queries
    all_queries = {}
    all_queries.update(get_competence_queries())

    # Execute all queries
    for description, query in all_queries.items():
        execute_query(g, description, query)


if __name__ == "__main__":
    main()
