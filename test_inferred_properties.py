#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Проверка выводимых свойств автомобилей
"""

from owlready2 import *

# Загружаем онтологию
onto = get_ontology("file://cars_ontology.owl").load()

def test_inferred_properties():
    """Проверяет наличие выводимых свойств у автомобилей"""
    
    print("="*80)
    print("ПРОВЕРКА ВЫВОДИМЫХ СВОЙСТВ")
    print("="*80)
    
    vehicles = list(onto.Vehicle.instances())
    print(f"\nВсего автомобилей: {len(vehicles)}")
    
    # Проверяем наличие свойств
    has_reliability = 0
    has_efficiency = 0
    has_sportiness = 0
    has_family = 0
    has_value = 0
    
    sample_vehicles = []
    
    for vehicle in vehicles[:20]:  # Первые 20 для примера
        if hasattr(vehicle, 'ReliabilityScore') and vehicle.ReliabilityScore:
            has_reliability += 1
            if len(sample_vehicles) < 5:
                sample_vehicles.append(vehicle)
        
        if hasattr(vehicle, 'FuelEfficiencyLevel') and vehicle.FuelEfficiencyLevel:
            has_efficiency += 1
        
        if hasattr(vehicle, 'SportinessLevel') and vehicle.SportinessLevel:
            has_sportiness += 1
        
        if hasattr(vehicle, 'FamilyFriendlinessScore') and vehicle.FamilyFriendlinessScore:
            has_family += 1
        
        if hasattr(vehicle, 'ValueForMoneyScore') and vehicle.ValueForMoneyScore:
            has_value += 1
    
    print(f"\nВ первых 20 автомобилях:")
    print(f"  ReliabilityScore: {has_reliability}")
    print(f"  FuelEfficiencyLevel: {has_efficiency}")
    print(f"  SportinessLevel: {has_sportiness}")
    print(f"  FamilyFriendlinessScore: {has_family}")
    print(f"  ValueForMoneyScore: {has_value}")
    
    # Показываем примеры
    if sample_vehicles:
        print("\n" + "="*80)
        print("ПРИМЕРЫ АВТОМОБИЛЕЙ С ВЫВОДИМЫМИ СВОЙСТВАМИ")
        print("="*80)
        
        for vehicle in sample_vehicles[:3]:
            name = vehicle.name.replace('_', ' ')
            print(f"\n{name}:")
            
            if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
                print(f"  Производитель: {vehicle.MadeBy[0].name.replace('_', ' ')}")
            
            if hasattr(vehicle, 'Year') and vehicle.Year:
                print(f"  Год: {vehicle.Year}")
            
            if hasattr(vehicle, 'ReliabilityScore') and vehicle.ReliabilityScore:
                print(f"  ⭐ Надежность: {vehicle.ReliabilityScore}/10")
            
            if hasattr(vehicle, 'FuelEfficiencyLevel') and vehicle.FuelEfficiencyLevel:
                print(f"  ⛽ Экономичность: {vehicle.FuelEfficiencyLevel}")
            
            if hasattr(vehicle, 'SportinessLevel') and vehicle.SportinessLevel:
                print(f"  🏎️ Спортивность: {vehicle.SportinessLevel}")
            
            if hasattr(vehicle, 'FamilyFriendlinessScore') and vehicle.FamilyFriendlinessScore:
                print(f"  👨‍👩‍👧‍👦 Семейность: {vehicle.FamilyFriendlinessScore}/10")
            
            if hasattr(vehicle, 'ValueForMoneyScore') and vehicle.ValueForMoneyScore:
                print(f"  💰 Соотношение цена/качество: {vehicle.ValueForMoneyScore}/10")
            
            if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
                print(f"  🛡️ Рейтинг безопасности: {vehicle.OverallCrashRating}/5")
            
            if hasattr(vehicle, 'MSRP') and vehicle.MSRP:
                print(f"  💵 Цена: ${vehicle.MSRP:,.0f}")


if __name__ == "__main__":
    test_inferred_properties()

