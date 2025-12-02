#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SPARQL запросы с использованием выводимых свойств
"""

from owlready2 import *
import re

# Загружаем онтологию
onto = get_ontology("file://cars_ontology.owl").load()

# Базовый namespace
BASE_NS = "http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#"

def clean_name_for_display(name: str) -> str:
    """Преобразует имя из формата онтологии в читаемый формат"""
    return name.replace('_', ' ')

def execute_sparql(query: str, description: str):
    """Выполняет SPARQL запрос и выводит результаты"""
    print(f"\n{'='*80}")
    print(f"Вопрос: {description}")
    print(f"{'='*80}")
    
    try:
        results = list(default_world.sparql(query))
        
        if not results:
            print("Результаты не найдены.")
            return
        
        print(f"\nНайдено автомобилей: {len(results)}\n")
        
        # Выводим первые 10 результатов
        for idx, result in enumerate(results[:10], 1):
            vehicle = result[0]
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
            
            # Выводимые свойства
            if hasattr(vehicle, 'ReliabilityScore') and vehicle.ReliabilityScore:
                print(f"   ⭐ Надежность: {vehicle.ReliabilityScore}/10")
            
            if hasattr(vehicle, 'FuelEfficiencyLevel') and vehicle.FuelEfficiencyLevel:
                print(f"   ⛽ Экономичность: {vehicle.FuelEfficiencyLevel}")
            
            if hasattr(vehicle, 'SportinessLevel') and vehicle.SportinessLevel:
                print(f"   🏎️ Спортивность: {vehicle.SportinessLevel}")
            
            if hasattr(vehicle, 'FamilyFriendlinessScore') and vehicle.FamilyFriendlinessScore:
                print(f"   👨‍👩‍👧‍👦 Семейность: {vehicle.FamilyFriendlinessScore}/10")
            
            if hasattr(vehicle, 'ValueForMoneyScore') and vehicle.ValueForMoneyScore:
                print(f"   💰 Соотношение цена/качество: {vehicle.ValueForMoneyScore}/10")
            
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
            
            print()
        
        if len(results) > 10:
            print(f"... и еще {len(results) - 10} автомобилей\n")
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        import traceback
        traceback.print_exc()


# Запрос 1: Автомобиль для перевозки детей (используем FamilyFriendlinessScore)
query1 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :FamilyFriendlinessScore ?familyScore .
    FILTER (?familyScore >= 7.0)
}}
ORDER BY DESC(?familyScore)
LIMIT 20
"""

# Запрос 2: Экономичный автомобиль (используем FuelEfficiencyLevel)
query2 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :FuelEfficiencyLevel ?efficiency .
    FILTER (
        ?efficiency = "Very High" || 
        ?efficiency = "High"
    )
}}
LIMIT 20
"""

# Запрос 3: Спортивные автомобили (используем SportinessLevel)
query3 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :SportinessLevel ?sportiness .
    ?vehicle :MSRP ?price .
    FILTER (
        (?sportiness = "Very High" || ?sportiness = "High") &&
        ?price <= 50000
    )
}}
ORDER BY DESC(?sportiness) ASC(?price)
LIMIT 20
"""

# Запрос 4: Надежный автомобиль премиум-класса (используем ReliabilityScore)
query4 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :hasSegment ?segment .
    ?vehicle :ReliabilityScore ?reliability .
    FILTER (
        regex(str(?segment), "Luxury", "i") &&
        ?reliability >= 7.0
    )
}}
ORDER BY DESC(?reliability)
LIMIT 20
"""

# Запрос 5: Лучшее соотношение цена/качество (используем ValueForMoneyScore)
query5 = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <{BASE_NS}>

SELECT DISTINCT ?vehicle
WHERE {{
    ?vehicle rdf:type :Vehicle .
    ?vehicle :ValueForMoneyScore ?value .
    ?vehicle :MSRP ?price .
    FILTER (
        ?value >= 7.0 &&
        ?price <= 20000
    )
}}
ORDER BY DESC(?value) ASC(?price)
LIMIT 20
"""


def main():
    """Выполняет все SPARQL запросы с выводимыми свойствами"""
    
    print("="*80)
    print("SPARQL ЗАПРОСЫ С ВЫВОДИМЫМИ СВОЙСТВАМИ")
    print("="*80)
    
    # Выполняем все запросы
    execute_sparql(query1, 
                   "Мне нужен автомобиль для перевозки детей (по FamilyFriendlinessScore)")
    
    execute_sparql(query2,
                   "Ищу экономичный автомобиль (по FuelEfficiencyLevel)")
    
    execute_sparql(query3,
                   "Люблю скорость, но бюджет ограничен (по SportinessLevel)")
    
    execute_sparql(query4,
                   "Ищу надежный автомобиль премиум-класса (по ReliabilityScore)")
    
    execute_sparql(query5,
                   "Бюджет до 20000, лучшее соотношение цена/качество (по ValueForMoneyScore)")
    
    print("\n" + "="*80)
    print("Все запросы выполнены!")
    print("="*80)


if __name__ == "__main__":
    main()

