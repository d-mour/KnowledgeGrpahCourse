#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Добавление выводимых (inferred) свойств для автомобилей на основе существующих данных
"""

from owlready2 import *
import statistics
from typing import Optional

# Загружаем онтологию
onto = get_ontology("file://cars_ontology.owl").load()

with onto:
    # Добавляем новые выводимые свойства
    class ReliabilityScore(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [float]
        comment = ["Оценка надежности от 0 до 10, вычисляется на основе рейтинга безопасности, года выпуска и популярности"]
    
    class FuelEfficiencyLevel(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [str]
        comment = ["Уровень экономичности: 'Very High', 'High', 'Medium', 'Low', 'Very Low'"]
    
    class SportinessLevel(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [str]
        comment = ["Уровень спортивности: 'Very High', 'High', 'Medium', 'Low', 'Very Low'"]
    
    class FamilyFriendlinessScore(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [float]
        comment = ["Оценка семейности от 0 до 10, на основе безопасности, багажника и количества дверей"]
    
    class ValueForMoneyScore(DataProperty, FunctionalProperty):
        domain = [onto.Vehicle]
        range = [float]
        comment = ["Оценка соотношения цена/качество от 0 до 10"]


def calculate_reliability_score(vehicle) -> Optional[float]:
    """
    Вычисляет надежность на основе:
    - Рейтинга безопасности (40% веса)
    - Года выпуска (30% веса) - более новые = надежнее
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
    
    # Год выпуска (2011-2017, нормализуем к 0-10)
    if hasattr(vehicle, 'Year') and vehicle.Year:
        year = int(vehicle.Year)
        # 2011 = 0, 2017 = 10
        year_score = ((year - 2011) / 6.0) * 10.0
        score += year_score * 0.3
        weight += 0.3
    else:
        score += 5.0 * 0.3
        weight += 0.3
    
    # Популярность (нормализуем к 0-10)
    if hasattr(vehicle, 'Popularity') and vehicle.Popularity:
        popularity = int(vehicle.Popularity)
        # Предполагаем, что популярность от 0 до 10000
        # Нормализуем к 0-10
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
    # Чем меньше литров на 100 км, тем экономичнее
    l_per_100km = 235.2 / avg_mpg
    
    # Определяем уровень на основе литров на 100 км
    if l_per_100km <= 5.9:  # <= 5.9 l/100km (очень экономично, ~40+ MPG)
        return "Very High"
    elif l_per_100km <= 7.8:  # <= 7.8 l/100km (экономично, ~30+ MPG)
        return "High"
    elif l_per_100km <= 11.8:  # <= 11.8 l/100km (средне, ~20+ MPG)
        return "Medium"
    elif l_per_100km <= 15.7:  # <= 15.7 l/100km (неэкономично, ~15+ MPG)
        return "Low"
    else:  # > 15.7 l/100km (очень неэкономично, <15 MPG)
        return "Very Low"


def get_body_style_sportiness_score(body_style_name: str) -> float:
    """
    Возвращает балл спортивности для типа кузова (0-3 балла)
    Учитывает ВСЕ типы кузова с разными весами
    """
    body_lower = body_style_name.lower()
    
    # Очень спортивные (3 балла)
    if 'convertible' in body_lower and 'suv' not in body_lower:
        return 3.0
    if 'coupe' in body_lower:
        return 3.0
    
    # Спортивные (2 балла)
    if 'convertible_suv' in body_lower:
        return 2.0
    if '2dr' in body_lower and ('hatchback' in body_lower or 'suv' in body_lower):
        return 2.0
    
    # Средне спортивные (1.5 балла)
    if '4dr_hatchback' in body_lower:
        return 1.5
    if 'wagon' in body_lower:
        return 1.0
    
    # Обычные (0.5 балла)
    if 'sedan' in body_lower:
        return 0.5
    if '4dr_suv' in body_lower or '2dr_suv' in body_lower:
        return 0.5
    
    # Менее спортивные (0.25 балла)
    if 'pickup' in body_lower:
        return 0.25
    
    # Не спортивные (0 баллов)
    if 'minivan' in body_lower or 'van' in body_lower:
        return 0.0
    
    # По умолчанию для неизвестных типов
    return 0.0


def get_segment_sportiness_score(segment_name: str) -> float:
    """
    Возвращает балл спортивности для сегмента рынка (0-3 балла)
    Учитывает ВСЕ сегменты с разными весами
    """
    segment_lower = segment_name.lower()
    
    # Максимально спортивные (3 балла)
    if 'high-performance' in segment_lower or 'exotic' in segment_lower:
        return 3.0
    
    # Очень спортивные (2.5 балла)
    if 'performance' in segment_lower or 'factory_tuner' in segment_lower:
        return 2.5
    
    # Спортивные (1.5 балла)
    if 'luxury' in segment_lower:
        return 1.5
    
    # Средне спортивные (1 балл)
    if 'crossover' in segment_lower:
        return 1.0
    
    # Обычные (0.5 балла)
    if 'hatchback' in segment_lower:
        return 0.5
    
    # Не спортивные (0 баллов)
    if 'hybrid' in segment_lower or 'diesel' in segment_lower or 'flex_fuel' in segment_lower:
        return 0.0
    if segment_lower == 'na':
        return 0.0
    
    # По умолчанию для неизвестных сегментов
    return 0.0


def calculate_sportiness_level(vehicle) -> Optional[str]:
    """
    Определяет уровень спортивности на основе:
    - Мощности двигателя (0-5 баллов)
    - Сегмента рынка (0-3 балла) - учитывает ВСЕ сегменты
    - Типа кузова (0-3 балла) - учитывает ВСЕ типы кузова
    """
    hp = None
    if hasattr(vehicle, 'EngineHP') and vehicle.EngineHP:
        hp = int(vehicle.EngineHP)
    
    # Собираем все сегменты и берем максимальный балл
    segment_score = 0.0
    if hasattr(vehicle, 'hasSegment') and vehicle.hasSegment:
        for segment in vehicle.hasSegment:
            seg_score = get_segment_sportiness_score(segment.name)
            segment_score = max(segment_score, seg_score)
    
    # Получаем балл для типа кузова
    body_score = 0.0
    if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
        body_style = vehicle.StyledAs[0].name
        body_score = get_body_style_sportiness_score(body_style)
    
    # Вычисляем оценку
    score = 0.0
    
    # Мощность (0-5 баллов)
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
    
    # Сегмент (0-3 балла)
    score += segment_score
    
    # Тип кузова (0-3 балла)
    score += body_score
    
    # Определяем уровень (максимум 11 баллов)
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
    """
    Вычисляет семейность на основе:
    - Рейтинга безопасности (40%)
    - Объема багажника (30%)
    - Количества дверей (30%)
    """
    score = 0.0
    weight = 0.0
    
    # Рейтинг безопасности
    if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
        rating = float(vehicle.OverallCrashRating)
        score += (rating / 5.0) * 10.0 * 0.4
        weight += 0.4
    else:
        score += 5.0 * 0.4
        weight += 0.4
    
    # Объем багажника (предполагаем 0-30 куб.фт)
    if hasattr(vehicle, 'TrunkVolume') and vehicle.TrunkVolume:
        trunk = float(vehicle.TrunkVolume)
        trunk_score = min((trunk / 30.0) * 10.0, 10.0)
        score += trunk_score * 0.3
        weight += 0.3
    else:
        score += 5.0 * 0.3
        weight += 0.3
    
    # Количество дверей (4-5 дверей лучше для семьи)
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


def calculate_value_for_money_score(vehicle) -> Optional[float]:
    """
    Вычисляет соотношение цена/качество на основе:
    - Цены (чем дешевле при хороших характеристиках, тем лучше)
    - Рейтинга безопасности
    - Мощности
    - Расхода топлива
    """
    if not hasattr(vehicle, 'MSRP') or not vehicle.MSRP:
        return None
    
    price = float(vehicle.MSRP)
    if price <= 0:
        return None
    
    # Базовые характеристики
    rating = 0
    if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
        rating = float(vehicle.OverallCrashRating)
    
    hp = 0
    if hasattr(vehicle, 'EngineHP') and vehicle.EngineHP:
        hp = int(vehicle.EngineHP)
    
    # Средний расход (чем меньше, тем лучше)
    avg_mpg = None
    if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG and hasattr(vehicle, 'HighwayMPG') and vehicle.HighwayMPG:
        avg_mpg = (float(vehicle.CityMPG) + float(vehicle.HighwayMPG)) / 2.0
    elif hasattr(vehicle, 'CityMPG') and vehicle.CityMPG:
        avg_mpg = float(vehicle.CityMPG)
    elif hasattr(vehicle, 'HighwayMPG') and vehicle.HighwayMPG:
        avg_mpg = float(vehicle.HighwayMPG)
    
    # Вычисляем "ценность" (value)
    value = 0.0
    
    # Рейтинг безопасности (0-5 -> 0-3 балла)
    value += (rating / 5.0) * 3.0
    
    # Мощность (нормализуем, 0-500 л.с. -> 0-3 балла)
    if hp > 0:
        value += min((hp / 500.0) * 3.0, 3.0)
    
    # Экономичность (чем меньше литров на 100 км, тем лучше, 0-4 балла)
    if avg_mpg:
        # Конвертируем MPG в литры на 100 км
        l_per_100km = 235.2 / avg_mpg
        # Нормализуем: <= 5.9 l/100km = 4, <= 7.8 = 3, <= 11.8 = 2, <= 15.7 = 1
        if l_per_100km <= 5.9:
            value += 4.0
        elif l_per_100km <= 7.8:
            value += 3.0
        elif l_per_100km <= 11.8:
            value += 2.0
        elif l_per_100km <= 15.7:
            value += 1.0
    
    # Вычисляем соотношение ценность/цена
    # Нормализуем цену: $2000 = 1, $50000 = 10
    normalized_price = min((price / 50000.0) * 10.0, 10.0)
    
    # Score = (value / normalized_price) * 10, но ограничиваем максимумом 10
    if normalized_price > 0:
        score = min((value / normalized_price) * 10.0, 10.0)
    else:
        score = 0.0
    
    return round(score, 2)


def add_inferred_properties(limit: Optional[int] = None):
    """Добавляет выводимые свойства ко всем автомобилям"""
    
    print("="*80)
    print("ДОБАВЛЕНИЕ ВЫВОДИМЫХ СВОЙСТВ К АВТОМОБИЛЯМ")
    print("="*80)
    
    vehicles = list(onto.Vehicle.instances())
    total = len(vehicles)
    
    if limit:
        vehicles = vehicles[:limit]
        print(f"Обработка первых {limit} из {total} автомобилей...")
    else:
        print(f"Обработка всех {total} автомобилей...")
    
    processed = 0
    updated = 0
    
    for idx, vehicle in enumerate(vehicles):
        if idx % 500 == 0:
            print(f"Обработано: {idx}/{len(vehicles)}, обновлено: {updated}")
        
        with onto:
            # Надежность
            reliability = calculate_reliability_score(vehicle)
            if reliability is not None:
                vehicle.ReliabilityScore = reliability
                updated += 1
            
            # Экономичность
            efficiency = calculate_fuel_efficiency_level(vehicle)
            if efficiency:
                vehicle.FuelEfficiencyLevel = efficiency
            
            # Спортивность
            sportiness = calculate_sportiness_level(vehicle)
            if sportiness:
                vehicle.SportinessLevel = sportiness
            
            # Семейность
            family_score = calculate_family_friendliness_score(vehicle)
            if family_score is not None:
                vehicle.FamilyFriendlinessScore = family_score
            
            # Соотношение цена/качество
            value_score = calculate_value_for_money_score(vehicle)
            if value_score is not None:
                vehicle.ValueForMoneyScore = value_score
        
        processed += 1
    
    print(f"\nОбработка завершена!")
    print(f"Обработано автомобилей: {processed}")
    print(f"Обновлено с новыми свойствами: {updated}")
    
    # Сохраняем онтологию
    output_file = "cars_ontology.owl"
    print(f"\nСохраняю онтологию в файл {output_file}...")
    onto.save(file=output_file, format="rdfxml")
    print("Готово!")


if __name__ == "__main__":
    import sys
    
    limit = None
    if len(sys.argv) > 1 and '--limit' in sys.argv:
        limit_idx = sys.argv.index('--limit')
        if limit_idx + 1 < len(sys.argv):
            limit = int(sys.argv[limit_idx + 1])
    
    add_inferred_properties(limit=limit)

