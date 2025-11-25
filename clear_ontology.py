#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from owlready2 import *

onto = get_ontology("file://ontology.rdf").load()

print("Начинаю очистку онтологии от всех сущностей...")

classes_to_clear = [
    onto.Vehicle,
    onto.Manufacturer,
    onto.BodyStyle,
    onto.Transmission,
    onto.MarketSegment,
    onto.Engine,
    onto.SafetySystem,
    onto.Country,
    onto.CrashTest
]

total_removed = 0

with onto:
    for cls in classes_to_clear:
        instances = list(cls.instances())
        count = len(instances)
        for instance in instances:
            destroy_entity(instance)
        total_removed += count
        if count > 0:
            print(f"Удалено {count} экземпляров класса {cls.name}")

print(f"\nВсего удалено сущностей: {total_removed}")

output_file = "ontology.rdf"
print(f"\nСохраняю очищенную онтологию в файл {output_file}...")
onto.save(file=output_file, format="rdfxml")
print("Готово! Онтология очищена, структура (классы и свойства) сохранена.")

