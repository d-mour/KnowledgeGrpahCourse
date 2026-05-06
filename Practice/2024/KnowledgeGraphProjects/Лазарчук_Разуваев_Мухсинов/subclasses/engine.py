import pandas as pd
import re
def clean_displacement(row):
    if pd.isna(row['Displacement']):
        return row
    if isinstance(row['Displacement'], str):
        row['Displacement'] = str(row['Displacement']).replace(' cc', '')
    row['Displacement'] = int(row['Displacement'])
    return row

def clean_power(row):
    if pd.isna(row['Power']):
        return row
    power_value = row['Power']
    if isinstance(power_value, (int, float)):
        return row
    match = re.search(r"(?P<power>\d+\.?\d*)\s*(PS|bhp|hp)?", str(power_value), re.IGNORECASE)
    if match:
        ans = match.group("power")
        row['Power'] = float(ans)
    else:
        row['Power'] = nan
    return row

def clean_torque(row):
    if pd.isna(row['Torque']):
        return row
    torque_value = row['Torque']
    if isinstance(torque_value, (int, float)):
        return row
    match = re.search(r"(?P<torque>\d+\.?\d*)", str(torque_value), re.IGNORECASE)
    if match:
        row['Torque'] = float(match.group("torque"))
    else:
        row['Torque'] = np.nan
    return row

def clean(row):
    row = clean_displacement(row)
    row = clean_power(row)
    row = clean_torque(row)
    return row