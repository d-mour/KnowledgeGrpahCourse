#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import re
import time
from owlready2 import * 
import requests
from typing import Optional, Dict, Any

onto = get_ontology("file://ontology.rdf").load()

with onto:
    class ID(DataProperty, FunctionalProperty):
        pass
    
    class Year(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [int]
    
    class EngineHP(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [int]
    
    class EngineCylinders(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [int]
    
    class EngineFuelType(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [str]
    
    class DriveType(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [str]
    
    class NumberOfDoors(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [int]
    
    class HighwayMPG(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [float]
    
    class CityMPG(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [float]
    
    class MSRP(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [float]
    
    class Popularity(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [int]
    
    class OverallCrashRating(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [int]
    
    class TrunkVolume(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [float]
    
    class VehicleSize(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [str]

def clean_name(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name

def get_carapi_data(make: str, model: str, year: int, api_token: Optional[str] = None, api_secret: Optional[str] = None) -> Dict[str, Any]:
    if not api_token or not api_secret:
        return {}
    
    try:
        login_url = "https://carapi.app/api/auth/login"
        login_payload = {
            "api_token": api_token,
            "api_secret": api_secret
        }
        login_headers = {
            "accept": "text/plain",
            "Content-Type": "application/json"
        }
        
        login_response = requests.post(login_url, json=login_payload, headers=login_headers, timeout=10)
        
        if login_response.status_code != 200:
            return {}
        
        jwt_token = login_response.json().get('access_token')
        if not jwt_token:
            return {}
        
        search_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        search_url = f"https://carapi.app/api/models"
        search_params = {
            "make": make,
            "model": model,
            "year": year
        }
        
        search_response = requests.get(search_url, headers=search_headers, params=search_params, timeout=10)
        
        if search_response.status_code == 200:
            data = search_response.json()
            if isinstance(data, dict) and 'data' in data and len(data['data']) > 0:
                car_data = data['data'][0]
                result = {}
                
                if 'safety_rating' in car_data:
                    result['safety_rating'] = float(car_data['safety_rating'])
                elif 'nhtsa_rating' in car_data:
                    result['safety_rating'] = float(car_data['nhtsa_rating'])
                
                if 'trunk_volume' in car_data:
                    result['trunk_volume'] = float(car_data['trunk_volume'])
                elif 'cargo_volume' in car_data:
                    result['trunk_volume'] = float(car_data['cargo_volume'])
                
                return result
        
        time.sleep(0.5)
        return {}
    
    except Exception as e:
        print(f"Ошибка при запросе к CarAPI для {make} {model} {year}: {e}")
        return {}

def safe_int(value: str) -> Optional[int]:
    try:
        return int(float(value)) if value and value.strip() else None
    except (ValueError, TypeError):
        return None

def safe_float(value: str) -> Optional[float]:
    try:
        return float(value) if value and value.strip() else None
    except (ValueError, TypeError):
        return None

def populate_ontology(csv_file: str = "cars.csv", 
                     output_file: str = "cars_ontology.owl",
                     use_carapi: bool = False,
                     api_token: Optional[str] = None,
                     api_secret: Optional[str] = None,
                     limit: Optional[int] = None):
    
    manufacturers = {}
    body_styles = {}
    transmissions = {}
    market_segments = {}
    engines = {}
    countries = {}

    countries_manufacturers = {
        "Japan": ["Toyota", "Honda", "Nissan", "Mazda", "Subaru", "Lexus", "Infiniti", "Mitsubishi", "Suzuki", "Isuzu", "Daihatsu", "Mazda", "Subaru", "Lexus", "Infiniti", "Mitsubishi", "Suzuki", "Isuzu", "Daihatsu", "Scion", "Acura"],
        "Germany": ["BMW", "Mercedes-Benz", "Audi", "Volkswagen", "Opel", "Maybach", "Porsche", "Bugatti"],
        "USA": ["Ford", "Chevrolet", "Dodge", "Ram", "GMC", "Jeep", "Tesla", "Chrysler", "Lincoln", "Buick", "Cadillac", "Plymouth", "Oldsmobile", "Pontiac", "HUMMER"],
        "UK": ["McLaren", "Alfa Romeo", "Lotus", "Aston Martin", "Rolls-Royce", "Land Rover", "Bentley"],
        "Korea": ["Hyundai", "Kia", "Ssangyong", "Genesis"],
        "Italy": ["Ferrari", "Lamborghini", "Maserati", "FIAT", "Lancia"],
        "Sweden": ["Koenigsegg", "Volvo", "Saab"],
        "Netherlands": ["Spyker"],
    }
    
    def find_country_for_manufacturer(manufacturer_name: str) -> Optional[str]:
        for country, manufacturer_list in countries_manufacturers.items():
            if manufacturer_name in manufacturer_list:
                return country
        return None
    
    processed_count = 0
    skipped_count = 0
    
    print(f"Начинаю обработку файла {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader):
            if limit and idx >= limit:
                break
            
            if idx % 100 == 0:
                print(f"Обработано записей: {idx}, создано автомобилей: {processed_count}")
            
            make = row.get('Make', '').strip()
            model = row.get('Model', '').strip()
            year_str = row.get('Year', '').strip()
            
            if not make or not model or not year_str:
                skipped_count += 1
                continue
            
            year = safe_int(year_str)
            if not year:
                skipped_count += 1
                continue
            
            csv_id = idx + 1
            
            existing_vehicle = None
            for v in onto.Vehicle.instances():
                if hasattr(v, 'ID') and v.ID == csv_id:
                    existing_vehicle = v
                    break
            
            if existing_vehicle:
                continue
            
            vehicle_name = f"{clean_name(make)}_{clean_name(model)}_{year}_{csv_id}"
            
            with onto:
                if make not in manufacturers:
                    manufacturer_name = clean_name(make)
                    manufacturer = onto.Manufacturer(manufacturer_name)
                    manufacturer.ID = len(manufacturers) + 1
                    manufacturers[make] = manufacturer
                    
                    country_name = find_country_for_manufacturer(make)
                    if country_name:
                        country_clean = clean_name(country_name)
                        if country_name not in countries:
                            country = onto.Country(country_clean)
                            country.ID = len(countries) + 1
                            countries[country_name] = country
                        else:
                            country = countries[country_name]
                        manufacturer.WhereIs = [country]
                else:
                    manufacturer = manufacturers[make]
                
                vehicle = onto.Vehicle(vehicle_name)
                vehicle.ID = csv_id
                vehicle.MadeBy = [manufacturer]
                
                vehicle.Year = year
                
                body_style_name = row.get('Vehicle Style', '').strip()
                if body_style_name:
                    if body_style_name not in body_styles:
                        body_style_clean = clean_name(body_style_name)
                        body_style = onto.BodyStyle(body_style_clean)
                        body_style.ID = len(body_styles) + 1
                        body_styles[body_style_name] = body_style
                    else:
                        body_style = body_styles[body_style_name]
                    vehicle.StyledAs = [body_style]
                
                vehicle_size = row.get('Vehicle Size', '').strip()
                if vehicle_size:
                    vehicle.VehicleSize = vehicle_size
                
                transmission_type = row.get('Transmission Type', '').strip()
                if transmission_type:
                    if transmission_type not in transmissions:
                        transmission_clean = clean_name(transmission_type)
                        transmission = onto.Transmission(transmission_clean)
                        transmission.ID = len(transmissions) + 1
                        transmissions[transmission_type] = transmission
                    else:
                        transmission = transmissions[transmission_type]
                    vehicle.hasTransmission = [transmission]
                
                market_category = row.get('Market Category', '').strip()
                if market_category:
                    categories = [c.strip() for c in market_category.split(',')]
                    for category in categories:
                        if category:
                            if category not in market_segments:
                                segment_clean = clean_name(category)
                                segment = onto.MarketSegment(segment_clean)
                                segment.ID = len(market_segments) + 1
                                market_segments[category] = segment
                            else:
                                segment = market_segments[category]
                            if not hasattr(vehicle, 'hasSegment') or not vehicle.hasSegment:
                                vehicle.hasSegment = []
                            vehicle.hasSegment.append(segment)
                
                engine_hp = safe_int(row.get('Engine HP', ''))
                if engine_hp:
                    vehicle.EngineHP = engine_hp
                
                engine_cylinders = safe_int(row.get('Engine Cylinders', ''))
                if engine_cylinders:
                    vehicle.EngineCylinders = engine_cylinders
                
                engine_fuel_type = row.get('Engine Fuel Type', '').strip()
                if engine_fuel_type:
                    vehicle.EngineFuelType = engine_fuel_type
                
                if engine_hp or engine_cylinders or engine_fuel_type:
                    engine_name = f"engine_{clean_name(make)}_{engine_hp}_{engine_cylinders}_{clean_name(engine_fuel_type)}"
                    if engine_name not in engines:
                        engine = onto.Engine(engine_name)
                        engine.ID = len(engines) + 1
                        engine.MadeBy = [manufacturer]
                        engines[engine_name] = engine
                    else:
                        engine = engines[engine_name]
                    vehicle.hasEngine = [engine]
                
                drive_type = row.get('Driven_Wheels', '').strip()
                if drive_type:
                    vehicle.DriveType = drive_type
                
                num_doors = safe_int(row.get('Number of Doors', ''))
                if num_doors:
                    vehicle.NumberOfDoors = num_doors
                
                highway_mpg = safe_float(row.get('highway MPG', ''))
                if highway_mpg:
                    vehicle.HighwayMPG = highway_mpg
                
                city_mpg = safe_float(row.get('city mpg', ''))
                if city_mpg:
                    vehicle.CityMPG = city_mpg
                
                msrp = safe_float(row.get('MSRP', ''))
                if msrp:
                    vehicle.MSRP = msrp
                
                popularity = safe_int(row.get('Popularity', ''))
                if popularity:
                    vehicle.Popularity = popularity
                
                if use_carapi and api_token and api_secret:
                    carapi_data = get_carapi_data(make, model, year, api_token, api_secret)
                    if 'trunk_volume' in carapi_data:
                        vehicle.TrunkVolume = carapi_data['trunk_volume']
            
            processed_count += 1
    
    print(f"\nОбработка завершена!")
    print(f"Создано автомобилей: {processed_count}")
    print(f"Пропущено записей: {skipped_count}")
    print(f"Создано производителей: {len(manufacturers)}")
    print(f"Создано стран: {len(countries)}")
    print(f"Создано типов кузова: {len(body_styles)}")
    print(f"Создано трансмиссий: {len(transmissions)}")
    print(f"Создано рыночных сегментов: {len(market_segments)}")
    print(f"Создано двигателей: {len(engines)}")
    
    print(f"\nСохраняю онтологию в файл {output_file}...")
    onto.save(file=output_file, format="rdfxml")
    print("Готово!")

if __name__ == "__main__":
    import sys
    
    use_api = False
    api_token = None
    api_secret = None
    limit = None
    
    if len(sys.argv) > 1:
        if '--api' in sys.argv:
            use_api = True
            api_token = input("Введите CarAPI токен: ").strip()
            api_secret = input("Введите CarAPI секрет: ").strip()
        
        if '--limit' in sys.argv:
            limit_idx = sys.argv.index('--limit')
            if limit_idx + 1 < len(sys.argv):
                limit = int(sys.argv[limit_idx + 1])
    
    populate_ontology(
        csv_file="cars.csv",
        output_file="cars_ontology.owl",
        use_carapi=use_api,
        api_token=api_token,
        api_secret=api_secret,
        limit=limit
    )

