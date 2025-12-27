import csv
import os

def run(args):
    input_file = './parsed_csv/enemies.csv'
    output_file = './parsed_csv/enemies_processed.csv'
    

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        writer.writerow(['Name', 'Vulnerables'])
        
        elements = ['Pyro', 'Hydro', 'Electro', 'Cryo', 'Dendro', 'Anemo', 'Geo']
        
        for row in reader:
            name = row['Name']
            resistances = []
            

            for element in elements:
                res_value = row[f'RES {element}']
                resistances.append((element, res_value))
            

            numeric_values = []
            for element, value in resistances:
                if value.endswith('%') and not value.startswith('Immune'):
                    try:
                        numeric_value = float(value.strip('%'))
                        numeric_values.append(numeric_value)
                    except ValueError:
                        continue
            

            if not numeric_values:
                continue
                

            min_resistance = min(numeric_values)
            

            vulnerables = []
            for element, value in resistances:
                if value.endswith('%') and not value.startswith('Immune'):
                    try:
                        numeric_value = float(value.strip('%'))
                        if numeric_value == min_resistance:
                            vulnerables.append(element)
                    except ValueError:
                        continue
            

            if vulnerables:
                writer.writerow([name, ', '.join(vulnerables)])