#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
from owlready2 import *
import requests
from typing import Optional, Dict, Any

onto = get_ontology("file://cars_ontology.owl").load()

def clean_name(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name

def get_nhtsa_crash_test_data(make: str, model: str, year: int, cache: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    cache_key = f"{make}_{model}_{year}"
    
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        make_encoded = make.replace(' ', '%20')
        model_encoded = model.replace(' ', '%20')
        
        search_url = f"https://api.nhtsa.gov/SafetyRatings/modelyear/{year}/make/{make_encoded}/model/{model_encoded}?format=json"
        
        search_response = requests.get(search_url, timeout=10)
        
        if search_response.status_code != 200:
            cache[cache_key] = {}
            return {}
        
        search_data = search_response.json()
        
        if not search_data.get('Results') or len(search_data['Results']) == 0:
            cache[cache_key] = {}
            return {}
        
        first_vehicle_id = search_data['Results'][0]['VehicleId']
        
        details_url = f"https://api.nhtsa.gov/SafetyRatings/VehicleId/{first_vehicle_id}?format=json"
        
        details_response = requests.get(details_url, timeout=10)
        
        if details_response.status_code != 200:
            cache[cache_key] = {}
            return {}
        
        details_data = details_response.json()
        
        if not details_data.get('Results') or len(details_data['Results']) == 0:
            cache[cache_key] = {}
            return {}
        
        result_data = details_data['Results'][0]
        
        crash_data = {}
        
        if result_data.get('OverallRating') and result_data['OverallRating'] != "Not Rated":
            try:
                crash_data['overall_rating'] = int(result_data['OverallRating'])
            except (ValueError, TypeError):
                pass
        
        cache[cache_key] = crash_data
        time.sleep(0.3)
        
        return crash_data
    
    except Exception as e:
        print(f"Ошибка при запросе к NHTSA API для {make} {model} {year}: {e}")
        cache[cache_key] = {}
        return {}

def populate_crash_ratings(ontology_file: str = "cars_ontology.owl",
                           output_file: str = "cars_ontology.owl",
                           limit: Optional[int] = None):
    
    nhtsa_cache = {}
    processed_count = 0
    updated_count = 0
    skipped_count = 0
    
    print(f"Начинаю заполнение рейтингов краш-тестов из NHTSA API...")
    print(f"Загружено автомобилей в онтологии: {len(list(onto.Vehicle.instances()))}")
    
    vehicles = list(onto.Vehicle.instances())
    
    for idx, vehicle in enumerate(vehicles):
        if limit and idx >= limit:
            break
        
        if idx % 100 == 0:
            print(f"Обработано: {idx}/{len(vehicles)}, обновлено: {updated_count}, пропущено: {skipped_count}")
        
        if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
            skipped_count += 1
            continue
        
        if not hasattr(vehicle, 'MadeBy') or not vehicle.MadeBy:
            skipped_count += 1
            continue
        
        manufacturer = vehicle.MadeBy[0]
        make = manufacturer.name.replace('_', ' ')
        
        if not hasattr(vehicle, 'Year') or not vehicle.Year:
            skipped_count += 1
            continue
        
        year = vehicle.Year
        
        vehicle_name_parts = vehicle.name.split('_')
        if len(vehicle_name_parts) < 2:
            skipped_count += 1
            continue
        
        model_parts = vehicle_name_parts[1:-2]
        model = ' '.join(model_parts).replace('_', ' ')
        
        with onto:
            nhtsa_data = get_nhtsa_crash_test_data(make, model, year, nhtsa_cache)
            if nhtsa_data and 'overall_rating' in nhtsa_data:
                vehicle.OverallCrashRating = nhtsa_data['overall_rating']
                updated_count += 1
        
        processed_count += 1
    
    print(f"\nОбработка завершена!")
    print(f"Обработано автомобилей: {processed_count}")
    print(f"Обновлено рейтингов: {updated_count}")
    print(f"Пропущено (уже есть рейтинг или нет данных): {skipped_count}")
    print(f"Уникальных запросов к API: {len(nhtsa_cache)}")
    
    print(f"\nСохраняю онтологию в файл {output_file}...")
    onto.save(file=output_file, format="rdfxml")
    print("Готово!")

if __name__ == "__main__":
    import sys
    
    limit = None
    
    if len(sys.argv) > 1:
        if '--limit' in sys.argv:
            limit_idx = sys.argv.index('--limit')
            if limit_idx + 1 < len(sys.argv):
                limit = int(sys.argv[limit_idx + 1])
    
    populate_crash_ratings(
        ontology_file="cars_ontology.owl",
        output_file="cars_ontology.owl",
        limit=limit
    )

