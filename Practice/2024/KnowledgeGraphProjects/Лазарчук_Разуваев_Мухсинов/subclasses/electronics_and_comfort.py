import pandas as pd

def clean_cruise_control(row):
    if row['Cruise_Control'] == 'Yes':
        row['Cruise_Control'] = True
    return row

def clean_power_steering(row):
    if isinstance(row['Power_Steering'], str):
        row['Power_Steering'] = True
    return row

def clean(row):
    row = clean_cruise_control(row)
    row = clean_power_steering(row)
    return row