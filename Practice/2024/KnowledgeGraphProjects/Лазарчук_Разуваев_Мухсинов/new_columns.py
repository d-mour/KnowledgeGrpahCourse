import pandas as pd
import numpy as np
def add_price_category(df):
    price_bins = [0, 1500000, 5000000, 10000000, float('inf')]
    price_labels = ['Budget', 'Mid-Range', 'Premium', 'Luxury']
    df['Price_Category'] = pd.cut(df['Ex-Showroom_Price'], bins=price_bins, labels=price_labels)
    return df

def add_offroad_capability(df):
    def calculate_offroad_capability(row):
        score = 0

        # Тип кузова
        if row['Body_Type'] in ['SUV', 'Crossover', 'Pick-up']:
            score += 2
        elif row['Body_Type'] in ['Hatchback', 'Sedan']:
            score -= 1
        elif row['Body_Type'] in ['Coupe', 'Convertible', 'Sports']:
            score -= 2
        elif row['Body_Type'] == 'MPV':
            score -= 1
        elif row['Body_Type'] == 'MUV':
            score += 1

        if pd.notna(row['Ground_Clearance']):
            if row['Ground_Clearance'] >= 200:
                score += 2
            elif row['Ground_Clearance'] < 150:
                score -= 1

        if row['Drivetrain'] in ['AWD', '4WD']:
            score += 2
        elif row['Drivetrain'] in ['FWD', 'RWD']:
            score -= 1

        if pd.notna(row['Wheelbase']):
            if row['Wheelbase'] < 2600:
                score += 1
            elif row['Wheelbase'] > 2800:
                score -= 1

        if pd.notna(row['Torque']):
            if row['Torque'] >= 300:
                score += 2
            elif row['Torque'] < 200:
                score -= 1

        if pd.notna(row['Kerb_Weight']):
            if row['Kerb_Weight'] > 2000:
                score -= 1
            elif 1500 <= row['Kerb_Weight'] <= 2000:
                score += 1

        if score >= 6:
            return 'High'
        elif 3 <= score < 6:
            return 'Medium'
        else:
            return 'Low'

    df['Offroad_Capability'] = df.apply(calculate_offroad_capability, axis=1)
    return df

def add_car_dimensions(df):
    def calculate_car_dimensions(row):
        if pd.notna(row['Length']) and pd.notna(row['Width']) and pd.notna(row['Height']):
            volume = row['Length'] / 1000 * row['Width'] / 1000 * row['Height'] / 1000
            if volume >= 19:
                return 'Large'
            elif 14 < volume < 19:
                return 'Middle'
            else:
                return 'Small'
        else:
            return np.nan

    df['Car_Dimensions'] = df.apply(calculate_car_dimensions, axis=1)
    return df


