from subclasses import appearance, cars, electronics_and_comfort, engine, safety, transmission
import new_columns
from new_columns import add_offroad_capability
from new_columns import add_car_dimensions
import pandas as pd

old_cars = pd.read_csv('resource/cars.csv')

cars_column = ['Make', 'Model', 'Variant', 'Body_Type', 'Seating_Capacity', 'Ex-Showroom_Price', 'Fuel_Type', 'Wheelbase']
appearance_columns = ['Length', 'Width', 'Height', 'Boot_Space', 'Doors', 'Ground_Clearance', 'Kerb_Weight']
electronics_and_comfort_columns = ['Cruise_Control', 'Power_Steering']
engine_columns = ['Displacement', 'Power', 'Torque']
safety_columns = ['ABS_(Anti-lock_Braking_System)', 'Airbags']
suspensions_and_brakes_columns = ['Front_Brakes', 'Front_Suspension', 'Rear_Brakes', 'Rear_Suspension']
transmission_columns = ['Drivetrain', 'Gears']

all_columns = (cars_column + appearance_columns +
               electronics_and_comfort_columns +
               engine_columns + safety_columns +
               suspensions_and_brakes_columns +
               transmission_columns)

cars_df = old_cars[all_columns]

cars_df = cars_df[cars_df['Boot_Space'] != "209(All3RowsUp).550(3rdRowFolded)&803(2ndRowand3rdRowFolded) litres"]

cars_df = cars_df.apply(cars.clean, axis=1)
cars_df = cars_df.apply(appearance.clean, axis=1)
cars_df = cars_df.apply(electronics_and_comfort.clean, axis=1)
cars_df = cars_df.apply(engine.clean, axis=1)
cars_df = cars_df.apply(safety.clean, axis=1)
cars_df = cars_df.apply(transmission.clean, axis=1)

cars_df = new_columns.add_price_category(cars_df)
cars_df = add_offroad_capability(cars_df)
cars_df = add_car_dimensions(cars_df)

new_column_names = {
    'Make': 'Company',
    'Model': 'Model',
    'Variant': 'Variant',
    'Body_Type': 'Type',
    'Seating_Capacity': 'Seating_Capacity',
    'Ex-Showroom_Price': 'Price',
    'Fuel_Type': 'Fuel_Type',
    'Wheelbase': 'Wheelbase',
    'Length': 'Length',
    'Width': 'Width',
    'Height': 'Height',
    'Boot_Space': 'Boot_Space',
    'Doors': 'Doors',
    'Ground_Clearance': 'Ground_Clearance',
    'Kerb_Weight': 'Kerb_Weight',
    'Cruise_Control': 'Cruise_Control',
    'Power_Steering': 'Power_Steering',
    'Displacement': 'Displacement',
    'Power': 'Power',
    'Torque': 'Torque',
    'ABS_(Anti-lock_Braking_System)': 'ABS',
    'Airbags': 'Airbags',
    'Front_Brakes': 'Front_Brakes',
    'Front_Suspension': 'Front_Suspension',
    'Rear_Brakes': 'Rear_Brakes',
    'Rear_Suspension': 'Rear_Suspension',
    'Drivetrain': 'Drivetrain',
    'Gears': 'Gears',
    'Price_Category': 'Price_Category',
    'Offroad_Capability': 'Offroad_Capability',
    'Car_Dimensions': 'Car_Dimensions'
}
cars_df.rename(columns=new_column_names, inplace=True)

cars_df.to_csv('resource/new_cars.csv', index=False)

# unique_models = cars_df['Car_Dimensions'].unique()
# print(unique_models)
#
# for _, row in cars_df.iterrows():
#     if str(row['Car_Dimensions']) == 'Middle':
#         print(row['Make'] + " --- " + row['Model'] + " " + str(row['Car_Dimensions']))
    # if not isinstance(row['Wheelbase'], str):
    #     print('Wheelbase: ' + str(row['Wheelbase']) )
#
# print(cars_df.head())
# print(cars_df.info())

# first_row = cars_df.iloc[323]
# print("First row details:\n")
# for column, value in first_row.items():
#     print(f"{column}: {value}")
