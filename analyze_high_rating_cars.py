#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Анализ характеристик автомобилей с высоким рейтингом безопасности
"""

from owlready2 import *
from collections import Counter
import statistics

# Загружаем онтологию
onto = get_ontology("file://cars_ontology.owl").load()

# Базовый namespace
BASE_NS = "http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#"

def analyze_high_rating_cars():
    """Анализирует характеристики автомобилей с высоким рейтингом безопасности"""
    
    print("="*80)
    print("АНАЛИЗ ХАРАКТЕРИСТИК АВТОМОБИЛЕЙ С ВЫСОКИМ РЕЙТИНГОМ БЕЗОПАСНОСТИ")
    print("="*80)
    
    # Находим все автомобили с рейтингом >= 4
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX : <{BASE_NS}>

    SELECT DISTINCT ?vehicle ?rating
    WHERE {{
        ?vehicle rdf:type :Vehicle .
        ?vehicle :OverallCrashRating ?rating .
        FILTER (?rating >= 4)
    }}
    """
    
    results = list(default_world.sparql(query))
    
    print(f"\nНайдено автомобилей с рейтингом >= 4: {len(results)}")
    
    if not results:
        print("Автомобили с высоким рейтингом не найдены.")
        return
    
    # Собираем статистику
    manufacturers = []
    body_styles = []
    vehicle_sizes = []
    drive_types = []
    fuel_types = []
    hp_values = []
    city_mpg_values = []
    highway_mpg_values = []
    years = []
    ratings = []
    
    for vehicle_obj, rating in results:
        vehicle = vehicle_obj
        
        # Рейтинг
        if rating:
            ratings.append(int(rating))
        
        # Производитель
        if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
            manufacturer = vehicle.MadeBy[0].name.replace('_', ' ')
            manufacturers.append(manufacturer)
        
        # Тип кузова
        if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
            body_style = vehicle.StyledAs[0].name.replace('_', ' ')
            body_styles.append(body_style)
        
        # Размер автомобиля
        if hasattr(vehicle, 'VehicleSize') and vehicle.VehicleSize:
            vehicle_sizes.append(vehicle.VehicleSize)
        
        # Тип привода
        if hasattr(vehicle, 'DriveType') and vehicle.DriveType:
            drive_types.append(vehicle.DriveType)
        
        # Тип топлива
        if hasattr(vehicle, 'EngineFuelType') and vehicle.EngineFuelType:
            fuel_types.append(vehicle.EngineFuelType)
        
        # Мощность
        if hasattr(vehicle, 'EngineHP') and vehicle.EngineHP:
            hp_values.append(int(vehicle.EngineHP))
        
        # Расход топлива
        if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG:
            city_mpg_values.append(float(vehicle.CityMPG))
        
        if hasattr(vehicle, 'HighwayMPG') and vehicle.HighwayMPG:
            highway_mpg_values.append(float(vehicle.HighwayMPG))
        
        # Год
        if hasattr(vehicle, 'Year') and vehicle.Year:
            years.append(int(vehicle.Year))
    
    # Выводим статистику
    print("\n" + "="*80)
    print("СТАТИСТИКА ПО ХАРАКТЕРИСТИКАМ")
    print("="*80)
    
    # Производители
    if manufacturers:
        print("\n📊 ТОП-10 ПРОИЗВОДИТЕЛЕЙ:")
        manufacturer_counts = Counter(manufacturers)
        for manufacturer, count in manufacturer_counts.most_common(10):
            percentage = (count / len(manufacturers)) * 100
            print(f"   {manufacturer}: {count} ({percentage:.1f}%)")
    
    # Типы кузова
    if body_styles:
        print("\n🚗 ТОП-10 ТИПОВ КУЗОВА:")
        body_style_counts = Counter(body_styles)
        for body_style, count in body_style_counts.most_common(10):
            percentage = (count / len(body_styles)) * 100
            print(f"   {body_style}: {count} ({percentage:.1f}%)")
    
    # Размеры автомобилей
    if vehicle_sizes:
        print("\n📏 РАЗМЕРЫ АВТОМОБИЛЕЙ:")
        size_counts = Counter(vehicle_sizes)
        for size, count in size_counts.most_common():
            percentage = (count / len(vehicle_sizes)) * 100
            print(f"   {size}: {count} ({percentage:.1f}%)")
    
    # Типы привода
    if drive_types:
        print("\n⚙️ ТИПЫ ПРИВОДА:")
        drive_type_counts = Counter(drive_types)
        for drive_type, count in drive_type_counts.most_common():
            percentage = (count / len(drive_types)) * 100
            print(f"   {drive_type}: {count} ({percentage:.1f}%)")
    
    # Типы топлива
    if fuel_types:
        print("\n⛽ ТИПЫ ТОПЛИВА:")
        fuel_type_counts = Counter(fuel_types)
        for fuel_type, count in fuel_type_counts.most_common(10):
            percentage = (count / len(fuel_types)) * 100
            print(f"   {fuel_type}: {count} ({percentage:.1f}%)")
    
    # Числовые характеристики
    print("\n" + "="*80)
    print("ЧИСЛОВЫЕ ХАРАКТЕРИСТИКИ")
    print("="*80)
    
    if hp_values:
        print(f"\n💪 МОЩНОСТЬ (л.с.):")
        print(f"   Среднее: {statistics.mean(hp_values):.1f}")
        print(f"   Медиана: {statistics.median(hp_values):.1f}")
        print(f"   Минимум: {min(hp_values)}")
        print(f"   Максимум: {max(hp_values)}")
    
    if city_mpg_values:
        # Конвертируем MPG в l/100km
        city_l_values = [235.2 / mpg for mpg in city_mpg_values]
        print(f"\n🏙️ РАСХОД В ГОРОДЕ (l/100km):")
        print(f"   Среднее: {statistics.mean(city_l_values):.1f}")
        print(f"   Медиана: {statistics.median(city_l_values):.1f}")
        print(f"   Минимум: {min(city_l_values):.1f}")
        print(f"   Максимум: {max(city_l_values):.1f}")
    
    if highway_mpg_values:
        # Конвертируем MPG в l/100km
        highway_l_values = [235.2 / mpg for mpg in highway_mpg_values]
        print(f"\n🛣️ РАСХОД НА ТРАССЕ (l/100km):")
        print(f"   Среднее: {statistics.mean(highway_l_values):.1f}")
        print(f"   Медиана: {statistics.median(highway_l_values):.1f}")
        print(f"   Минимум: {min(highway_l_values):.1f}")
        print(f"   Максимум: {max(highway_l_values):.1f}")
    
    if years:
        print(f"\n📅 ГОДЫ ВЫПУСКА:")
        print(f"   Средний год: {statistics.mean(years):.0f}")
        print(f"   Самый старый: {min(years)}")
        print(f"   Самый новый: {max(years)}")
        year_counts = Counter(years)
        print(f"\n   ТОП-5 ЛЕТ ПО КОЛИЧЕСТВУ:")
        for year, count in year_counts.most_common(5):
            print(f"   {year}: {count} автомобилей")
    
    if ratings:
        print(f"\n⭐ РЕЙТИНГИ БЕЗОПАСНОСТИ:")
        rating_counts = Counter(ratings)
        for rating in sorted(rating_counts.keys(), reverse=True):
            count = rating_counts[rating]
            percentage = (count / len(ratings)) * 100
            print(f"   {rating}/5: {count} ({percentage:.1f}%)")
    
    print("\n" + "="*80)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*80)


if __name__ == "__main__":
    analyze_high_rating_cars()

