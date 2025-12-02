#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Анализ всех типов кузова и сегментов рынка в онтологии
"""

from owlready2 import *
from collections import Counter

onto = get_ontology("file://cars_ontology.owl").load()

print("="*80)
print("АНАЛИЗ ТИПОВ КУЗОВА И СЕГМЕНТОВ РЫНКА")
print("="*80)

# Собираем все типы кузова
body_styles = []
segments = []

for vehicle in onto.Vehicle.instances():
    if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
        body_style = vehicle.StyledAs[0].name
        body_styles.append(body_style)
    
    if hasattr(vehicle, 'hasSegment') and vehicle.hasSegment:
        for segment in vehicle.hasSegment:
            segments.append(segment.name)

print("\n📊 ВСЕ ТИПЫ КУЗОВА:")
body_style_counts = Counter(body_styles)
for body_style, count in body_style_counts.most_common():
    print(f"   {body_style}: {count}")

print("\n📊 ВСЕ СЕГМЕНТЫ РЫНКА:")
segment_counts = Counter(segments)
for segment, count in segment_counts.most_common():
    print(f"   {segment}: {count}")

