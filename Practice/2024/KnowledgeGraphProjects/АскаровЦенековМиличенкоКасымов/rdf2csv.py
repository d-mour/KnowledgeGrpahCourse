from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
import csv

g = Graph()
g.parse('output.rdf', format="xml")

def normalize(arr):
    norm_arr = []
    diff = 1
    diff_arr = max(max(arr),1)
    for i in arr:
        temp = ((i*diff)/diff_arr)
        norm_arr.append(temp)
    return norm_arr

def export_recipes_csv():
    # First query to get recipes, cuisines, and ingredients
    query_recipes = """
    PREFIX ex: <http://example.org/>

    SELECT ?recipe ?cuisine ?ingredient
    WHERE {
      ?recipe a ex:Product ;
              ex:typeOfProduct ex:Recipe ;
              ex:typeOfCuisine ?cuisine ;
              ex:hasIngredient ?ingredient .
    }
    """
    results = g.query(query_recipes)

    recipe2ingredient = {}
    recipe2cuisine = {}
    ingredient2vitamin = {}
    
    # Collect recipes and their ingredients
    for row in results:
        recipe_id = row.recipe.split('/')[-1]
        ingredient_id = row.ingredient.split('/')[-1]
        cuisine_id = row.cuisine.split('/')[-1]

        if recipe_id not in recipe2ingredient:
            recipe2ingredient[recipe_id] = []
        recipe2ingredient[recipe_id].append(ingredient_id)
        recipe2cuisine[recipe_id] = cuisine_id

    # Second query to get ingredients and their associated vitamins
    query_ingredients = """
    PREFIX ex: <http://example.org/>
    
    SELECT ?ingredient ?vitamin
    WHERE {
      ?ingredient a ex:Product ;
              ex:typeOfProduct ex:Ingredient ;
              ex:containsVitamin ?vitamin .
    }
    """
    results = g.query(query_ingredients)

    vitamins = []
    # Map ingredients to vitamins
    for row in results:
        ingredient_id = row.ingredient.split('/')[-1]
        vitamin_id = row.vitamin.split('/')[-1]
        if ingredient_id not in ingredient2vitamin:
            ingredient2vitamin[ingredient_id] = []
        if vitamin_id not in vitamins:
            vitamins.append(vitamin_id)
        ingredient2vitamin[ingredient_id].append(vitamin_id)
    
    vitamins.sort()
    
    # Remap list in ingredient2vitamin to csv-row-format
    for ingredient_id in ingredient2vitamin:
        list_of_vitamin = []
        for vitamin in vitamins:
            list_of_vitamin.append(1 if vitamin in ingredient2vitamin[ingredient_id] else 0)
        ingredient2vitamin[ingredient_id] = list_of_vitamin
    
    # suming all ingredient in recipe2ingredient
    for recipe_id in recipe2ingredient:
        list_of_vitamin = [0 for i in vitamins]
        for ingredient_id in recipe2ingredient[recipe_id]:
            if ingredient_id in ingredient2vitamin:
                list_of_vitamin = [x + y for x, y in zip(ingredient2vitamin[ingredient_id], list_of_vitamin)]
        recipe2ingredient[recipe_id] = normalize(list_of_vitamin)
    
    # Prepare CSV data
    csv_body = [['кухня'] + list(vitamins)]
    
    for recipe, vitamins in recipe2ingredient.items():
        csv_body.append([recipe2cuisine[recipe]] + vitamins)

    # Write to CSV
    with open('output.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"')
        writer.writerows(csv_body)

export_recipes_csv()
