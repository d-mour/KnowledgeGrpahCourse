#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SPARQL запросы для поиска автомобилей по различным критериям
С вычислением выводимых свойств на лету
"""

from owlready2 import *
import re
from typing import Optional

# Загружаем онтологию
onto = get_ontology("file://cars_ontology.owl").load()

# Базовый namespace
BASE_NS = "http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#"

def clean_name_for_display(name: str) -> str:
    """Преобразует имя из формата онтологии в читаемый формат"""
    return name.replace('_', ' ')

def extract_model_and_year(vehicle_name: str) -> tuple:
    """
    Извлекает модель и год из имени автомобиля
    Формат: Manufacturer_Model_Year_ID
    Возвращает: (manufacturer, model, year) или (None, None, None) если не удалось распарсить
    """
    parts = vehicle_name.split('_')
    if len(parts) >= 3:
        # Пытаемся найти год (обычно это число из 4 цифр)
        year = None
        year_idx = -1
        for i, part in enumerate(parts):
            if part.isdigit() and len(part) == 4 and 1900 <= int(part) <= 2100:
                year = int(part)
                year_idx = i
                break
        
        if year_idx > 0:
            manufacturer = parts[0]
            model_parts = parts[1:year_idx]
            model = '_'.join(model_parts)
            return (manufacturer, model, year)
    
    return (None, None, None)


# ============================================================================
# ФУНКЦИИ ВЫЧИСЛЕНИЯ ВЫВОДИМЫХ СВОЙСТВ
# ============================================================================

def calculate_reliability_score(vehicle) -> Optional[float]:
    """
    Вычисляет надежность на основе:
    - Рейтинга безопасности (40% веса)
    - Года выпуска (30% веса) - более новые = надежнее, но не наказываем старые
    - Популярности (30% веса) - популярные = надежнее
    """
    score = 0.0
    weight = 0.0
    
    # Рейтинг безопасности (0-5 -> 0-10)
    if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
        rating = float(vehicle.OverallCrashRating)
        score += (rating / 5.0) * 10.0 * 0.4
        weight += 0.4
    else:
        # Если нет рейтинга, даем средний балл
        score += 5.0 * 0.4
        weight += 0.4
    
    # Год выпуска (исправлено для старых автомобилей)
    if hasattr(vehicle, 'Year') and vehicle.Year:
        year = int(vehicle.Year)
        # Нормализуем: 1990-2017 -> 0-10
        # Для старых автомобилей (1990-2000) даем минимум 2 балла
        # Для новых (2011-2017) даем максимум 10 баллов
        if year < 2000:
            year_score = 2.0 + ((year - 1990) / 10.0) * 2.0  # 1990 = 2.0, 2000 = 4.0
        elif year < 2011:
            year_score = 4.0 + ((year - 2000) / 11.0) * 3.0  # 2000 = 4.0, 2011 = 7.0
        else:
            year_score = 7.0 + ((year - 2011) / 6.0) * 3.0  # 2011 = 7.0, 2017 = 10.0
        
        score += year_score * 0.3
        weight += 0.3
    else:
        score += 5.0 * 0.3
        weight += 0.3
    
    # Популярность (нормализуем к 0-10)
    if hasattr(vehicle, 'Popularity') and vehicle.Popularity:
        popularity = int(vehicle.Popularity)
        # Предполагаем, что популярность от 0 до 10000
        popularity_score = min((popularity / 10000.0) * 10.0, 10.0)
        score += popularity_score * 0.3
        weight += 0.3
    else:
        score += 5.0 * 0.3
        weight += 0.3
    
    if weight == 0:
        return None
    
    return round(score / weight, 2)


def calculate_fuel_efficiency_level(vehicle) -> Optional[str]:
    """
    Определяет уровень экономичности на основе CityMPG и HighwayMPG
    Использует литры на 100 км для вычисления
    """
    city_mpg = None
    highway_mpg = None
    
    if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG:
        city_mpg = float(vehicle.CityMPG)
    
    if hasattr(vehicle, 'HighwayMPG') and vehicle.HighwayMPG:
        highway_mpg = float(vehicle.HighwayMPG)
    
    if city_mpg is None and highway_mpg is None:
        return None
    
    # Используем среднее значение MPG, если есть оба
    if city_mpg and highway_mpg:
        avg_mpg = (city_mpg + highway_mpg) / 2.0
    elif city_mpg:
        avg_mpg = city_mpg
    else:
        avg_mpg = highway_mpg
    
    # Конвертируем MPG в литры на 100 км: 235.2 / MPG = l/100km
    l_per_100km = 235.2 / avg_mpg
    
    # Определяем уровень на основе литров на 100 км
    if l_per_100km <= 5.9:
        return "Very High"
    elif l_per_100km <= 7.8:
        return "High"
    elif l_per_100km <= 11.8:
        return "Medium"
    elif l_per_100km <= 15.7:
        return "Low"
    else:
        return "Very Low"


def get_body_style_sportiness_score(body_style_name: str) -> float:
    """Возвращает балл спортивности для типа кузова (0-3 балла)"""
    body_lower = body_style_name.lower()
    
    if 'convertible' in body_lower and 'suv' not in body_lower:
        return 3.0
    if 'coupe' in body_lower:
        return 3.0
    if 'convertible_suv' in body_lower:
        return 2.0
    if '2dr' in body_lower and ('hatchback' in body_lower or 'suv' in body_lower):
        return 2.0
    if '4dr_hatchback' in body_lower:
        return 1.5
    if 'wagon' in body_lower:
        return 1.0
    if 'sedan' in body_lower:
        return 0.5
    if '4dr_suv' in body_lower or '2dr_suv' in body_lower:
        return 0.5
    if 'pickup' in body_lower:
        return 0.25
    if 'minivan' in body_lower or 'van' in body_lower:
        return 0.0
    
    return 0.0


def get_segment_sportiness_score(segment_name: str) -> float:
    """Возвращает балл спортивности для сегмента рынка (0-3 балла)"""
    segment_lower = segment_name.lower()
    
    if 'high-performance' in segment_lower or 'exotic' in segment_lower:
        return 3.0
    if 'performance' in segment_lower or 'factory_tuner' in segment_lower:
        return 2.5
    if 'luxury' in segment_lower:
        return 1.5
    if 'crossover' in segment_lower:
        return 1.0
    if 'hatchback' in segment_lower:
        return 0.5
    if 'hybrid' in segment_lower or 'diesel' in segment_lower or 'flex_fuel' in segment_lower:
        return 0.0
    if segment_lower == 'na':
        return 0.0
    
    return 0.0


def calculate_sportiness_level(vehicle) -> Optional[str]:
    """Определяет уровень спортивности"""
    hp = None
    if hasattr(vehicle, 'EngineHP') and vehicle.EngineHP:
        hp = int(vehicle.EngineHP)
    
    segment_score = 0.0
    if hasattr(vehicle, 'hasSegment') and vehicle.hasSegment:
        for segment in vehicle.hasSegment:
            seg_score = get_segment_sportiness_score(segment.name)
            segment_score = max(segment_score, seg_score)
    
    body_score = 0.0
    if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
        body_style = vehicle.StyledAs[0].name
        body_score = get_body_style_sportiness_score(body_style)
    
    score = 0.0
    
    if hp:
        if hp >= 400:
            score += 5.0
        elif hp >= 300:
            score += 4.0
        elif hp >= 200:
            score += 3.0
        elif hp >= 150:
            score += 2.0
        elif hp >= 100:
            score += 1.0
    
    score += segment_score
    score += body_score
    
    if score >= 9.0:
        return "Very High"
    elif score >= 6.0:
        return "High"
    elif score >= 3.0:
        return "Medium"
    elif score >= 1.0:
        return "Low"
    else:
        return "Very Low"


def calculate_family_friendliness_score(vehicle) -> Optional[float]:
    """Вычисляет семейность на основе безопасности, багажника и количества дверей"""
    score = 0.0
    weight = 0.0
    
    if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
        rating = float(vehicle.OverallCrashRating)
        score += (rating / 5.0) * 10.0 * 0.4
        weight += 0.4
    else:
        score += 5.0 * 0.4
        weight += 0.4
    
    if hasattr(vehicle, 'TrunkVolume') and vehicle.TrunkVolume:
        trunk = float(vehicle.TrunkVolume)
        trunk_score = min((trunk / 30.0) * 10.0, 10.0)
        score += trunk_score * 0.3
        weight += 0.3
    else:
        score += 5.0 * 0.3
        weight += 0.3
    
    if hasattr(vehicle, 'NumberOfDoors') and vehicle.NumberOfDoors:
        doors = int(vehicle.NumberOfDoors)
        if doors >= 4:
            doors_score = 10.0
        elif doors == 3:
            doors_score = 7.0
        else:
            doors_score = 5.0
        score += doors_score * 0.3
        weight += 0.3
    else:
        score += 5.0 * 0.3
        weight += 0.3
    
    if weight == 0:
        return None
    
    return round(score / weight, 2)


# ============================================================================
# ФУНКЦИИ ДЛЯ ФИЛЬТРАЦИИ И ВЫВОДА
# ============================================================================

def get_vehicle_score(vehicle, query_type: str = "default") -> float:
    """Вычисляет оценку автомобиля для выбора лучшего варианта"""
    score = 0.0
    
    if query_type == "family":
        if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
            score += float(vehicle.OverallCrashRating) * 2.0
        if hasattr(vehicle, 'TrunkVolume') and vehicle.TrunkVolume:
            score += float(vehicle.TrunkVolume) * 0.5
        family_score = calculate_family_friendliness_score(vehicle)
        if family_score:
            score += family_score * 1.0
    
    if query_type == "economy":
        if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG:
            score += float(vehicle.CityMPG) * 1.0
        if hasattr(vehicle, 'HighwayMPG') and vehicle.HighwayMPG:
            score += float(vehicle.HighwayMPG) * 0.5
        efficiency = calculate_fuel_efficiency_level(vehicle)
        if efficiency:
            if efficiency == "Very High":
                score += 10.0
            elif efficiency == "High":
                score += 7.0
            elif efficiency == "Medium":
                score += 5.0
    
    if query_type == "sport":
        if hasattr(vehicle, 'EngineHP') and vehicle.EngineHP:
            score += float(vehicle.EngineHP) * 0.01
        sportiness = calculate_sportiness_level(vehicle)
        if sportiness:
            if sportiness == "Very High":
                score += 10.0
            elif sportiness == "High":
                score += 7.0
            elif sportiness == "Medium":
                score += 5.0
        if hasattr(vehicle, 'MSRP') and vehicle.MSRP:
            score -= float(vehicle.MSRP) * 0.0001
    
    if query_type == "premium" or query_type == "reliable":
        if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
            score += float(vehicle.OverallCrashRating) * 2.0
        reliability = calculate_reliability_score(vehicle)
        if reliability:
            score += reliability * 1.0
    
    if query_type == "value":
        if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
            score += float(vehicle.OverallCrashRating) * 1.0
        if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG:
            score += float(vehicle.CityMPG) * 0.5
        if hasattr(vehicle, 'MSRP') and vehicle.MSRP:
            score -= float(vehicle.MSRP) * 0.0001
    
    return score

def filter_unique_models(vehicles, query_type: str = "default") -> list:
    """Фильтрует дубликаты по модели и году, оставляя только лучший вариант"""
    model_groups = {}
    
    for vehicle in vehicles:
        vehicle_name = vehicle.name
        manufacturer, model, year = extract_model_and_year(vehicle_name)
        
        if manufacturer and model and year:
            key = f"{manufacturer}_{model}_{year}"
            
            if key not in model_groups:
                model_groups[key] = vehicle
            else:
                current_score = get_vehicle_score(vehicle, query_type)
                saved_score = get_vehicle_score(model_groups[key], query_type)
                
                if current_score > saved_score:
                    model_groups[key] = vehicle
        else:
            model_groups[vehicle_name] = vehicle
    
    return list(model_groups.values())

def execute_sparql(query: str, description: str, query_type: str = "default"):
    """Выполняет SPARQL запрос и выводит результаты"""
    print(f"\n{'='*80}")
    print(f"Вопрос: {description}")
    print(f"{'='*80}")
    
    try:
        results = list(default_world.sparql(query))
        
        if not results:
            print("Результаты не найдены.")
            return
        
        # Извлекаем автомобили из результатов
        vehicles = [result[0] for result in results]
        
        # Фильтруем дубликаты по модели и году
        unique_vehicles = filter_unique_models(vehicles, query_type)
        
        # Сортируем по оценке (лучшие первыми)
        unique_vehicles.sort(key=lambda v: get_vehicle_score(v, query_type), reverse=True)
        
        print(f"\nНайдено автомобилей: {len(results)}")
        print(f"Уникальных моделей: {len(unique_vehicles)}")
        print(f"Показываем лучшие 10 уникальных моделей:\n")
        
        # Выводим первые 10 уникальных результатов
        for idx, vehicle in enumerate(unique_vehicles[:10], 1):
            vehicle_name = clean_name_for_display(vehicle.name)
            
            print(f"{idx}. {vehicle_name}")
            
            # Получаем дополнительные свойства
            if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
                manufacturer = clean_name_for_display(vehicle.MadeBy[0].name)
                print(f"   Производитель: {manufacturer}")
            
            if hasattr(vehicle, 'Year') and vehicle.Year:
                print(f"   Год: {vehicle.Year}")
            
            if hasattr(vehicle, 'MSRP') and vehicle.MSRP:
                print(f"   Цена: ${vehicle.MSRP:,.0f}")
            
            # Выводимые свойства (вычисляются на лету)
            reliability = calculate_reliability_score(vehicle)
            if reliability:
                print(f"   ⭐ Надежность: {reliability}/10")
            
            efficiency = calculate_fuel_efficiency_level(vehicle)
            if efficiency:
                print(f"   ⛽ Экономичность: {efficiency}")
            
            sportiness = calculate_sportiness_level(vehicle)
            if sportiness:
                print(f"   🏎️ Спортивность: {sportiness}")
            
            family_score = calculate_family_friendliness_score(vehicle)
            if family_score:
                print(f"   👨‍👩‍👧‍👦 Семейность: {family_score}/10")
            
            if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG:
                print(f"   Расход в городе: {round(235.2/vehicle.CityMPG, 1)} l/100km")
            
            if hasattr(vehicle, 'HighwayMPG') and vehicle.HighwayMPG:
                print(f"   Расход на трассе: {round(235.2/vehicle.HighwayMPG, 1)} l/100km")
            
            if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
                print(f"   Рейтинг безопасности: {vehicle.OverallCrashRating}/5")
            
            if hasattr(vehicle, 'TrunkVolume') and vehicle.TrunkVolume:
                print(f"   Объем багажника: {vehicle.TrunkVolume} куб.фт")
            
            if hasattr(vehicle, 'EngineHP') and vehicle.EngineHP:
                print(f"   Мощность: {vehicle.EngineHP} л.с.")
            
            if hasattr(vehicle, 'DriveType') and vehicle.DriveType:
                print(f"   Привод: {vehicle.DriveType}")
            
            if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
                body_style = clean_name_for_display(vehicle.StyledAs[0].name)
                print(f"   Тип кузова: {body_style}")
            
            print()
        
        if len(unique_vehicles) > 10:
            print(f"... и еще {len(unique_vehicles) - 10} уникальных моделей\n")
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# SPARQL ЗАПРОСЫ (увеличены LIMIT для получения большего разнообразия)
# ============================================================================

# Запрос 1: Автомобиль для перевозки детей
query1 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    OPTIONAL {{ ?vehicle :OverallCrashRating ?rating . }}
    OPTIONAL {{ ?vehicle :TrunkVolume ?trunk . }}
    FILTER (
        (!bound(?rating) || ?rating >= 4) &&
        (!bound(?trunk) || ?trunk >= 15.0)
    )
}}
ORDER BY DESC(?rating) DESC(?trunk)
LIMIT 100
"""

# Запрос 2: Экономичный автомобиль
query2 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :CityMPG ?cityMpg .
    FILTER (?cityMpg >= 25.0)
}}
ORDER BY DESC(?cityMpg)
LIMIT 100
"""

# Запрос 3: Спортивные автомобили
query3 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :EngineHP ?hp .
    ?vehicle :MSRP ?price .
    ?vehicle :hasSegment ?segment .
    FILTER (
        ?hp >= 200 &&
        ?price <= 50000 &&
        (regex(str(?segment), "High-Performance", "i") || 
         regex(str(?segment), "Performance", "i") ||
         regex(str(?segment), "Sport", "i"))
    )
}}
ORDER BY DESC(?hp) ASC(?price)
LIMIT 100
"""

# Запрос 4: Презентабельный для города
query4 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :hasSegment ?segment .
    ?vehicle :CityMPG ?cityMpg .
    FILTER (
        regex(str(?segment), "Luxury", "i") &&
        ?cityMpg >= 18.0
    )
}}
ORDER BY DESC(?cityMpg)
LIMIT 100
"""

# Запрос 5: Премиум надежный
query5 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :hasSegment ?segment .
    OPTIONAL {{ ?vehicle :OverallCrashRating ?rating . }}
    FILTER (
        regex(str(?segment), "Luxury", "i") &&
        (!bound(?rating) || ?rating >= 4)
    )
}}
ORDER BY DESC(?rating)
LIMIT 100
"""

# Запрос 6: Экономичный для мегаполиса
query6 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :CityMPG ?cityMpg .
    FILTER (?cityMpg >= 28.0)
}}
ORDER BY DESC(?cityMpg)
LIMIT 100
"""

# Запрос 7: Полный привод / Внедорожник
query7 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :DriveType ?driveType .
    OPTIONAL {{ ?vehicle :StyledAs ?bodyStyle . }}
    FILTER (
        (regex(str(?driveType), "all wheel drive", "i") || 
         regex(str(?driveType), "4wd", "i") ||
         regex(str(?driveType), "awd", "i")) &&
        (!bound(?bodyStyle) || 
         regex(str(?bodyStyle), "SUV", "i") ||
         regex(str(?bodyStyle), "Crossover", "i") ||
         regex(str(?bodyStyle), "Wagon", "i"))
    )
}}
LIMIT 100
"""

# Запрос 8: Бюджет до 20000
query8 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :MSRP ?price .
    ?vehicle :CityMPG ?cityMpg .
    ?vehicle :HighwayMPG ?highwayMpg .
    OPTIONAL {{ ?vehicle :OverallCrashRating ?rating . }}
    FILTER (
        ?price <= 20000 &&
        ?cityMpg >= 25.0 &&
        ?highwayMpg >= 30.0
    )
}}
ORDER BY DESC(?cityMpg) DESC(?highwayMpg) DESC(?rating)
LIMIT 100
"""


def main():
    """Выполняет все SPARQL запросы"""
    
    print("="*80)
    print("SPARQL ЗАПРОСЫ ДЛЯ ПОИСКА АВТОМОБИЛЕЙ")
    print("="*80)
    
    execute_sparql(query1, 
                   "Мне нужен автомобиль для перевозки детей, с высоким рейтингом безопасности и большим багажником",
                   query_type="family")
    
    execute_sparql(query2,
                   "Ищу экономичный автомобиль для ежедневных поездок на работу в пробках",
                   query_type="economy")
    
    execute_sparql(query3,
                   "Люблю скорость, но бюджет ограничен - какие спортивные автомобили доступны?",
                   query_type="sport")
    
    execute_sparql(query4,
                   "Нужен автомобиль для поездок по городу, чтобы выглядеть презентабельно на встречах",
                   query_type="premium")
    
    execute_sparql(query5,
                   "Ищу надежный автомобиль премиум-класса для спокойной езды",
                   query_type="reliable")
    
    execute_sparql(query6,
                   "Живу в мегаполисе с постоянными пробками, нужен экономичный автомобиль",
                   query_type="economy")
    
    execute_sparql(query7,
                   "Часто езжу по грунтовым дорогам, нужен автомобиль с полным приводом / Живу в селе, дороги плохие, нужен внедорожник или кроссовер",
                   query_type="default")
    
    execute_sparql(query8,
                   "Бюджет до 20000, нужен надежный автомобиль с низким расходом топлива",
                   query_type="value")
    
    print("\n" + "="*80)
    print("Все запросы выполнены!")
    print("="*80)


if __name__ == "__main__":
    main()
