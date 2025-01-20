import pandas as pd

def clean_abs(row):
    if row['ABS_(Anti-lock_Braking_System)'] == 'Yes':
        row['ABS_(Anti-lock_Braking_System)'] = True
    return row

def clean_airbags(row):
    if isinstance(row['Airbags'], str):
        row['Airbags'] = True
    return row

def clean(row):
    row = clean_abs(row)
    row = clean_airbags(row)
    return row