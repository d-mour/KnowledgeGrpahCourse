import pandas as pd
import re
import numpy as np

def clean_drivetrain(row):
    if pd.isna(row['Drivetrain']):
        return row
    drive_type = row['Drivetrain']
    match = re.search(r"\b(RWD|FWD|AWD|4WD)\b", str(drive_type), re.IGNORECASE)
    if match:
        row['Drivetrain'] = match.group(1).upper()
    else:
        row['Drivetrain'] = np.nan
    return row

def clean_gears(row):
    if pd.isna(row['Gears']):
        return row
    if 'Single Speed Reduction Gear' in row['Gears']:
        row['Gears'] = np.nan
        return row
    match = re.search(r"\b(\d+)\b", str(row['Gears']))
    if match:
        row['Gears'] = int(match.group(1))
    return row

def clean(row):
    row = clean_drivetrain(row)
    row = clean_gears(row)
    return row