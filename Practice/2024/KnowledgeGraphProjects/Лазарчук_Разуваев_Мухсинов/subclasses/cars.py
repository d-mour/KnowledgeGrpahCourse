import pandas as pd

def clean_mercedes(row):
    if 'Mercedes-Benz' in row['Model']:
        row['Model'] = row['Model'].replace('Mercedes-Benz ', '')
        row['Make'] = 'Mercedes-Benz'
    return row

def clean_rolls(row):
    if 'Rolls-Royce' in row['Model']:
        row['Model'] = row['Model'].replace('Rolls-Royce ', '')
        row['Make'] = 'Rolls-Royce'
    return row

def clean_datsun(row):
    if 'Datsun' in row['Variant']:
        row['Variant'] = row['Variant'].replace('Datsun ', '')
        row['Make'] = 'Datsun'
    return row

def clean_rr(row):
    if 'Land Rover Rover' in row['Make']:
        row['Make'] = 'Land Rover'
    return row

def clean_body_type(row):
    if not isinstance(row['Body_Type'], str) and row['Make'] == 'Porsche':
        row['Body_Type'] = 'Crossover'
    if not isinstance(row['Body_Type'], str) and row['Make'] == 'Maserati':
        row['Body_Type'] = 'Sports'
    if not isinstance(row['Body_Type'], str) and row['Make'] == 'Mahindra':
        row['Body_Type'] = 'Crossover'
    row['Body_Type'] = row['Body_Type'].split(',')[0]
    return row

def clean_price(row):
    row['Ex-Showroom_Price'] = int(float(str(row['Ex-Showroom_Price']).replace('Rs. ', '').replace(',', '').strip()) * 1.22)
    return row

def clean_fuel(row):
    row['Fuel_Type'] = row['Fuel_Type'].replace('CNG + Petrol', 'CNGPetrol')
    return row

def clean_wheelbase(row):
    if isinstance(row['Wheelbase'], str):
        row['Wheelbase'] = str(row['Wheelbase']).replace(' mm', '')
    if not pd.isna(row['Wheelbase']):
        row['Wheelbase'] = int(row['Wheelbase'])
    return row

def clean(row):
    row = clean_mercedes(row)
    row = clean_rolls(row)
    row = clean_datsun(row)
    row = clean_rr(row)
    row = clean_body_type(row)
    row = clean_price(row)
    row = clean_fuel(row)
    row = clean_wheelbase(row)
    return row
