import pandas as pd
def clean_length(row):
    if isinstance(row['Length'], str):
        row['Length'] = str(row['Length']).replace(' mm', '')
    if "." in row['Length']:
        row['Length'] = int(row['Length'].replace(".", "")) * 10
    if not pd.isna(row['Length']):
        row['Length'] = int(row['Length'])
    return row

def clean_width(row):
    if pd.isna(row['Width']):
        return row
    if isinstance(row['Width'], str):
        row['Width'] = str(row['Width']).replace(' mm', '')
    if "." in row['Width']:
        row['Width'] = int(row['Width'].replace(".", ""))
    if not pd.isna(row['Width']):
        row['Width'] = int(row['Width'])
    return row

def clean_height(row):
    if pd.isna(row['Height']):
        return row
    if isinstance(row['Height'], str):
        row['Height'] = str(row['Height']).replace(' mm', '')
    if "." in row['Height']:
        row['Height'] = int(row['Height'].replace(".", ""))
    if not pd.isna(row['Height']):
        row['Height'] = int(row['Height'])
    return row

def clean_boot_space(row):
    if pd.isna(row['Boot_Space']):
        return row
    if isinstance(row['Boot_Space'], str):
        row['Boot_Space'] = str(row['Boot_Space']).replace(' litres', '')
    if "." in row['Boot_Space']:
        row['Boot_Space'] = row['Boot_Space'].replace(".5", "")
    if not pd.isna(row['Boot_Space']):
        row['Boot_Space'] = int(row['Boot_Space'])
    return row

def clean_ground_clearance(row):
    if pd.isna(row['Ground_Clearance']):
        return row
    if isinstance(row['Ground_Clearance'], str):
        row['Ground_Clearance'] = str(row['Ground_Clearance']).replace(' mm', '')
    if "." in row['Ground_Clearance']:
        row['Ground_Clearance'] = row['Ground_Clearance'].replace(".5", "")
    if not pd.isna(row['Ground_Clearance']):
        row['Ground_Clearance'] = int(row['Ground_Clearance'])
    return row

def clean_kerb_weight(row):
    if pd.isna(row['Kerb_Weight']):
        return row
    if "1053-1080" in row['Kerb_Weight']:
        row['Kerb_Weight'] = "1080"
    if "1016-1043" in row['Kerb_Weight']:
        row['Kerb_Weight'] = "1043"
    if isinstance(row['Kerb_Weight'], str):
        row['Kerb_Weight'] = str(row['Kerb_Weight']).replace(' kg', '')
    if "." in row['Kerb_Weight']:
        row['Kerb_Weight'] = row['Kerb_Weight'].replace(".5", "")
    if not pd.isna(row['Kerb_Weight']):
        row['Kerb_Weight'] = int(row['Kerb_Weight'])
    return row
def clean(row):
    row = clean_length(row)
    row = clean_width(row)
    row = clean_height(row)
    row = clean_boot_space(row)
    row = clean_ground_clearance(row)
    row = clean_kerb_weight(row)
    return row
