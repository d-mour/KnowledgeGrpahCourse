from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

# Загружаем граф
g = Graph()
g.parse("all_experiments.ttl", format="turtle")

print("=" * 80)
print("SPARQL ЗАПРОСЫ К ЭКСПЕРИМЕНТАЛЬНЫМ ДАННЫМ")
print("=" * 80)


# ============================================================
# ЗАПРОС 1: Фазы и режимы для каждого эксперимента
# ============================================================
print("\n1. Фазы и режимы для каждого эксперимента:")
print("-" * 50)

query1 = """
PREFIX ex: <http://example.org/experiment/>
PREFIX phase: <http://example.org/phase/>
PREFIX mode: <http://example.org/mode/>

SELECT ?experiment ?id ?phase_label ?phase_start ?phase_end ?mode_label ?mode_start ?mode_end
WHERE {
    ?experiment a ex:Experiment ;
                ex:hasId ?id .

    OPTIONAL {
        ?experiment ex:hasPhase ?phase .
        ?phase phase:label ?phase_label ;
               phase:startTime ?phase_start ;
               phase:endTime ?phase_end .
    }

    OPTIONAL {
        ?experiment ex:hasMode ?mode .
        ?mode mode:label ?mode_label ;
              mode:startTime ?mode_start ;
              mode:endTime ?mode_end .
    }
}
ORDER BY ?id ?phase_start ?mode_start
"""

current_exp = None
for i, row in enumerate(g.query(query1)):
    if current_exp != row.id:
        if current_exp is not None:
            print()
        print(f"  Эксперимент {row.id}:")
        current_exp = row.id

    if row.phase_label:
        start_val = float(row.phase_start) if row.phase_start else 0
        end_val = float(row.phase_end) if row.phase_end else 0
        print(f"    Фаза: {row.phase_label} с {start_val:.2f} по {end_val:.2f} сек")
    if row.mode_label:
        start_val = float(row.mode_start) if row.mode_start else 0
        end_val = float(row.mode_end) if row.mode_end else 0
        print(f"    Режим: {row.mode_label} с {start_val:.2f} по {end_val:.2f} сек")

    if i == 5:
        break


# ============================================================
# ЗАПРОС 2: Все сигналы (изображения) в экспериментах
# ============================================================
print("\n2. Информация о сигналах (изображениях):")
print("-" * 50)

query2 = """
PREFIX ex: <http://example.org/experiment/>
PREFIX signal: <http://example.org/signal/>

SELECT ?experiment_id ?image_name ?width ?height
WHERE {
    ?exp a ex:Experiment ;
         ex:hasId ?experiment_id ;
         ex:hasSignal ?image .

    ?image signal:name ?image_name ;
           signal:width ?width ;
           signal:height ?height .
}
ORDER BY ?experiment_id
"""

for row in g.query(query2):
    print(f"  Эксперимент {row.experiment_id}: {row.image_name} ({row.width}x{row.height})")

# ============================================================
# ЗАПРОС 3: Эксперименты с хаотическими режимами
# ============================================================
print("\n3. Эксперименты, содержащие хаотические режимы:")
print("-" * 50)

query3 = """
PREFIX ex: <http://example.org/experiment/>
PREFIX mode: <http://example.org/mode/>

SELECT DISTINCT ?experiment_id ?mode_label ?mode_start ?mode_end
WHERE {
    ?exp a ex:Experiment ;
         ex:hasId ?experiment_id ;
         ex:hasMode ?mode .

    ?mode mode:label ?mode_label ;
          mode:startTime ?mode_start ;
          mode:endTime ?mode_end .

    FILTER(CONTAINS(LCASE(?mode_label), "chaotic"))
}
ORDER BY ?experiment_id ?mode_start
"""

for row in g.query(query3):
    start_val = float(row.mode_start) if row.mode_start else 0
    end_val = float(row.mode_end) if row.mode_end else 0
    print(f"  Эксперимент {row.experiment_id}: {row.mode_label} с {start_val:.2f} по {end_val:.2f} сек")

# ============================================================
# ЗАПРОС 4: Соотношение фаз и режимов во времени
# ============================================================
print("\n8. Временные интервалы фаз и режимов для эксперимента 0:")
print("-" * 50)

query4 = """
PREFIX ex: <http://example.org/experiment/>
PREFIX phase: <http://example.org/phase/>
PREFIX mode: <http://example.org/mode/>

SELECT ?phase_label ?phase_start ?phase_end ?mode_label ?mode_start ?mode_end
WHERE {
    ?exp a ex:Experiment ;
         ex:hasId 0 ;
         ex:hasPhase ?phase ;
         ex:hasMode ?mode .

    ?phase phase:label ?phase_label ;
           phase:startTime ?phase_start ;
           phase:endTime ?phase_end .

    ?mode mode:label ?mode_label ;
          mode:startTime ?mode_start ;
          mode:endTime ?mode_end .
}
ORDER BY ?phase_start ?mode_start
"""

print("  Фазы и режимы эксперимента 0:")
results = list(g.query(query4))
if results:
    for i, row in enumerate(results):
        phase_start = float(row.phase_start) if row.phase_start else 0
        phase_end = float(row.phase_end) if row.phase_end else 0
        mode_start = float(row.mode_start) if row.mode_start else 0
        mode_end = float(row.mode_end) if row.mode_end else 0
        print(f"    Фаза: {row.phase_label} [{phase_start:.2f}-{phase_end:.2f}]")
        print(f"    Режим: {row.mode_label} [{mode_start:.2f}-{mode_end:.2f}]")
        print()

        if i == 5:
            break
else:
    print("  Нет данных о фазах и режимах для эксперимента 0")

# ============================================================
# ЗАПРОС 5: Поиск аннотаций с определённым типом
# ============================================================
print("\n5. Аннотации типа 'box' в эксперименте 0:")
print("-" * 50)

query5 = """
PREFIX ex: <http://example.org/experiment/>
PREFIX signal: <http://example.org/signal/>
PREFIX ann: <http://example.org/annotation/>

SELECT ?label ?xtl ?ytl ?xbr ?ybr
WHERE {
    ?exp a ex:Experiment ;
         ex:hasId 0 ;
         ex:hasSignal ?image .

    ?image signal:hasAnnotation ?annotation .
    ?annotation ann:type "box" ;
                ann:label ?label ;
                ann:xtl ?xtl ;
                ann:ytl ?ytl ;
                ann:xbr ?xbr ;
                ann:ybr ?ybr .
}
LIMIT 10
"""

box_count = 0
for row in g.query(query5):
    xtl_val = float(row.xtl) if row.xtl else 0
    ytl_val = float(row.ytl) if row.ytl else 0
    xbr_val = float(row.xbr) if row.xbr else 0
    ybr_val = float(row.ybr) if row.ybr else 0
    print(f"  {row.label}: ({xtl_val:.2f}, {ytl_val:.2f}) → ({xbr_val:.2f}, {ybr_val:.2f})")
    box_count += 1

if box_count == 0:
    print("  Нет аннотаций типа 'box' в эксперименте 0")

# ============================================================
# ЗАПРОС 6: Общая статистика по всем аннотациям
# ============================================================
print("\n6. Общая статистика по всем аннотациям:")
print("-" * 50)

query6 = """
PREFIX ex: <http://example.org/experiment/>
PREFIX signal: <http://example.org/signal/>
PREFIX ann: <http://example.org/annotation/>

SELECT ?annotation_type (COUNT(?annotation) as ?total_count)
WHERE {
    ?exp a ex:Experiment ;
         ex:hasSignal ?image .

    ?image signal:hasAnnotation ?annotation .
    ?annotation ann:type ?annotation_type .
}
GROUP BY ?annotation_type
ORDER BY DESC(?total_count)
"""

for row in g.query(query6):
    print(f"  {row.annotation_type}: {row.total_count} шт.")

# ============================================================
# ЗАПРОС 7: Подробная информация о треках
# ============================================================
print("\n7. Детальная информация о треках в эксперименте 0:")
print("-" * 50)

query7 = """
PREFIX ex: <http://example.org/experiment/>
PREFIX ann: <http://example.org/annotation/>

SELECT ?track_label ?frame ?points
WHERE {
    ?exp a ex:Experiment ;
         ex:hasId 0 ;
         ex:hasTrack ?exp_track .

    ?exp_track ex:hasTrackAnnotation ?track .
    ?track ann:label ?track_label ;
           ann:hasShape ?shape .

    ?shape ann:frame ?frame ;
           ann:points ?points .
}
ORDER BY ?track_label ?frame
LIMIT 20
"""

track_count = 0
current_track = None
for row in g.query(query7):
    if current_track != row.track_label:
        if current_track is not None:
            print()
        print(f"  Трек: {row.track_label}")
        current_track = row.track_label
        track_count += 1

    points_preview = row.points[:50] + "..." if len(row.points) > 50 else row.points
    print(f"    Кадр {row.frame}: {points_preview}")

if track_count == 0:
    print("  Нет данных о треках для эксперимента 0")

print("\n" + "=" * 80)
print("Выполнение запросов завершено")
print("=" * 80)
