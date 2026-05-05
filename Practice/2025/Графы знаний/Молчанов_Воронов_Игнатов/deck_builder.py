"""
Система составления и анализа колод для Clash Royale на основе графа знаний.
Содержит компетентностные SPARQL-запросы для помощи в построении эффективных колод.
"""

from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

# Определяем пространства имён
CR = Namespace("http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#")

class DeckBuilder:
    """Класс для анализа и построения колод на основе графа знаний."""
    
    def __init__(self, ontology_file):
        """Загрузить онтологию."""
        print(f"Загрузка онтологии из {ontology_file}...")
        self.graph = Graph()
        self.graph.parse(ontology_file, format='turtle')
        self.graph.bind("cr", CR)
        print(f"Загружено {len(self.graph)} триплов\n")
    
    def query_1_hog_cycle_cards(self):
        """
        Вопрос 1: Какие карты, кроме "Всадника на кабане", часто используются 
        в архетипах быстрых колод ("Hog Cycle") для ускорения цикла и защиты?
        """
        print("=" * 80)
        print("ВОПРОС 1: Карты для Hog Cycle (ускорение цикла и защита)")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?name ?cost (GROUP_CONCAT(DISTINCT ?purpose; separator=", ") AS ?purposes)
        WHERE {
            ?card cr:используетсяВ cr:HogCycle .
            ?card rdfs:label ?name .
            ?card cr:стоимостьЭликсира ?cost .
            ?card cr:имеетНазначение ?purposeUri .
            ?purposeUri rdfs:label ?purpose .
            
            FILTER(?card != cr:HogRider)
            FILTER(?purposeUri = cr:УскорениеЦикла || ?purposeUri = cr:Защита)
        }
        GROUP BY ?name ?cost
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nНайдено карт: {len(results)}\n")
        for row in results:
            print(f"  • {row.name} ({row.cost} эликсира) - {row.purposes}")
        
        print("\n")
    
    def query_2_common_tactics(self):
        """
        Вопрос 2: Какими общими тактическими возможностями обладают 
        "Шахтер" и "Гоблинская бочка"?
        """
        print("=" * 80)
        print("ВОПРОС 2: Общие тактические возможности Шахтера и Гоблинской бочки")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?tactic
        WHERE {
            cr:Miner cr:обладаетТактическойВозможностью ?tacticUri .
            cr:GoblinBarrel cr:обладаетТактическойВозможностью ?tacticUri .
            ?tacticUri rdfs:label ?tactic .
        }
        """
        
        results = self.graph.query(query)
        
        print(f"\nОбщие тактические возможности:\n")
        for row in results:
            print(f"  • {row.tactic}")
        
        print("\n")
    
    def query_3_spawner_buildings(self):
        """
        Вопрос 3: Какие есть карты-здания, которые не атакуют юнитов напрямую, 
        а вместо этого создают их?
        """
        print("=" * 80)
        print("ВОПРОС 3: Здания-спаунеры (создающие юнитов)")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?name ?cost
        WHERE {
            ?building a cr:ЗданиеСпаунер .
            ?building rdfs:label ?name .
            OPTIONAL { ?building cr:стоимостьЭликсира ?cost }
        }
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nНайдено зданий-спаунеров: {len(results)}\n")
        for row in results:
            cost = f"{row.cost} эликсира" if row.cost else "неизвестно"
            print(f"  • {row.name} ({cost})")
        
        print("\n")
    
    def query_4_balloon_support(self):
        """
        Вопрос 4: Какие карты поддержки необходимы для успешной атаки "Воздушным шаром", 
        чтобы нейтрализовать его основные угрозы, такие как "Адская башня" или "Орда миньонов"?
        """
        print("=" * 80)
        print("ВОПРОС 4: Карты поддержки для Воздушного шара")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?name ?cost
        WHERE {
            cr:Balloon cr:требуетПоддержкиОт ?card .
            ?card rdfs:label ?name .
            OPTIONAL { ?card cr:стоимостьЭликсира ?cost }
        }
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nРекомендуемые карты поддержки: {len(results)}\n")
        for row in results:
            cost = f"{row.cost} эликсира" if row.cost else "неизвестно"
            print(f"  • {row.name} ({cost})")
        
        # Дополнительно показываем синергии
        query2 = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?name ?cost
        WHERE {
            cr:Balloon cr:хорошоСинергируетС ?card .
            ?card rdfs:label ?name .
            OPTIONAL { ?card cr:стоимостьЭликсира ?cost }
        }
        """
        
        results2 = self.graph.query(query2)
        
        if len(results2) > 0:
            print(f"\nДополнительные синергии:\n")
            for row in results2:
                cost = f"{row.cost} эликсира" if row.cost else "неизвестно"
                print(f"  • {row.name} ({cost})")
        
        print("\n")
    
    def query_5_elixir_collector_archetype(self):
        """
        Вопрос 5: Если противник ставит "Сборщик эликсира" в начале игры, 
        какие архетипы колод он, скорее всего, использует, и какой тип атаки следует ожидать?
        """
        print("=" * 80)
        print("ВОПРОС 5: Архетип колоды при использовании Сборщика эликсира")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?archetypeName ?avgCost ?attackType
        WHERE {
            cr:ElixirCollector cr:используетсяВ ?archetype .
            ?archetype rdfs:label ?archetypeName .
            OPTIONAL { ?archetype cr:средняяСтоимость ?avgCost }
            OPTIONAL { 
                ?archetype cr:архетипИмеетТипАтаки ?attackTypeUri .
                ?attackTypeUri rdfs:label ?attackType 
            }
        }
        """
        
        results = self.graph.query(query)
        
        print(f"\nВероятные архетипы:\n")
        for row in results:
            avg = f"(средняя стоимость: {row.avgCost})" if row.avgCost else ""
            attack = f" - {row.attackType}" if row.attackType else ""
            print(f"  • {row.archetypeName} {avg}{attack}")
        
        print("\n")
    
    def query_6_knight_replacement_anti_air(self):
        """
        Вопрос 6: Предложи замену для карты "Рыцарь" в колоде "Log Bait", 
        если сейчас популярны воздушные юниты, и данная карта должна их атаковать.
        """
        print("=" * 80)
        print("ВОПРОС 6: Замена Рыцаря с возможностью атаки воздушных целей")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?name ?cost ?role
        WHERE {
            ?card a cr:Войско .
            ?card rdfs:label ?name .
            ?card cr:стоимостьЭликсира ?cost .
            ?card cr:атакуетТипЦели ?target .
            
            # Должна атаковать воздушные цели
            FILTER(?target = cr:НаземныеИВоздушные || ?target = cr:Воздушные)
            
            # Похожая стоимость на Рыцаря (3 эликсира)
            FILTER(?cost >= 2 && ?cost <= 4)
            
            OPTIONAL {
                ?card cr:имеетРольВКолоде ?roleUri .
                ?roleUri rdfs:label ?role
            }
        }
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nВозможные замены для Рыцаря:\n")
        for row in results:
            role = f" - {row.role}" if row.role else ""
            print(f"  • {row.name} ({row.cost} эликсира){role}")
        
        # Проверяем прямую рекомендуемую замену
        query2 = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?name
        WHERE {
            cr:Knight cr:рекомендуемаяЗамена ?card .
            ?card rdfs:label ?name .
        }
        """
        
        results2 = self.graph.query(query2)
        
        if len(results2) > 0:
            print(f"\nПрямая рекомендация из онтологии:\n")
            for row in results2:
                print(f"  • {row.name}")
        
        print("\n")
    
    def query_7_cycle_cards_low_cost(self):
        """
        Вопрос 7: Какие карты стоимостью 1-2 эликсира можно использовать 
        для ускорения цикла колоды?
        """
        print("=" * 80)
        print("ВОПРОС 7: Карты для быстрого цикла (1-2 эликсира)")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?name ?cost (SAMPLE(?typeUri) AS ?cardType)
        WHERE {
            ?card rdfs:label ?name .
            ?card cr:стоимостьЭликсира ?cost .
            ?card a ?typeUri .
            
            FILTER(?cost <= 2)
            FILTER(?typeUri = cr:Войско || ?typeUri = cr:Заклинание)
        }
        GROUP BY ?name ?cost
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nКарты для цикла: {len(results)}\n")
        for row in results:
            card_type = str(row.cardType).split('#')[-1] if row.cardType else "Неизвестно"
            print(f"  • {row.name} ({row.cost} эликсира) - {card_type}")
        
        print("\n")
    
    def query_8_counter_cards(self):
        """
        Вопрос 8: Какие карты эффективно контрят "Орду миньонов" и "Адскую башню"?
        """
        print("=" * 80)
        print("ВОПРОС 8: Контр-карты против Орды миньонов и Адской башни")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?name ?cost
        WHERE {
            ?card cr:контрит ?target .
            ?card rdfs:label ?name .
            OPTIONAL { ?card cr:стоимостьЭликсира ?cost }
            
            FILTER(?target = cr:MinionHorde || ?target = cr:InfernoTower)
        }
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nКонтр-карты: {len(results)}\n")
        for row in results:
            cost = f"{row.cost} эликсира" if row.cost else "неизвестно"
            print(f"  • {row.name} ({cost})")
        
        print("\n")
    
    def query_9_synergy_pairs(self):
        """
        Вопрос 9: Какие пары карт имеют хорошую синергию друг с другом?
        """
        print("=" * 80)
        print("ВОПРОС 9: Пары карт с хорошей синергией")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?card1_name ?card2_name
        WHERE {
            ?card1 cr:хорошоСинергируетС ?card2 .
            ?card1 rdfs:label ?card1_name .
            ?card2 rdfs:label ?card2_name .
            
            # Избегаем дублирования (берем только одну сторону)
            FILTER(STR(?card1) < STR(?card2))
        }
        ORDER BY ?card1_name
        """
        
        results = self.graph.query(query)
        
        print(f"\nСинергичные пары: {len(results)}\n")
        for row in results:
            print(f"  • {row.card1_name} ↔ {row.card2_name}")
        
        print("\n")
    
    def query_10_direct_tower_damage(self):
        """
        Вопрос 10: Какие карты обладают способностью наносить прямой урон по башне?
        """
        print("=" * 80)
        print("ВОПРОС 10: Карты с прямым уроном по башне")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?name ?cost (SAMPLE(?typeUri) AS ?cardType)
        WHERE {
            ?card cr:обладаетТактическойВозможностью cr:ПрямойУронПоБашне .
            ?card rdfs:label ?name .
            ?card a ?typeUri .
            OPTIONAL { ?card cr:стоимостьЭликсира ?cost }
            
            # Фильтруем только основные типы карт
            FILTER(?typeUri = cr:Войско || ?typeUri = cr:Заклинание || ?typeUri = cr:Здание)
        }
        GROUP BY ?name ?cost
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nКарты с прямым уроном: {len(results)}\n")
        for row in results:
            cost = f"{row.cost} эликсира" if row.cost else "неизвестно"
            card_type = str(row.cardType).split('#')[-1] if row.cardType else "Неизвестно"
            print(f"  • {row.name} ({cost}) - {card_type}")
        
        print("\n")
    
    def query_11_defensive_buildings(self):
        """
        Вопрос 11: Какие оборонительные здания атакуют наземные цели и подходят для защиты?
        """
        print("=" * 80)
        print("ВОПРОС 11: Оборонительные здания для защиты от наземных войск")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?name ?cost ?targets
        WHERE {
            ?building a cr:ОборонительноеЗдание .
            ?building rdfs:label ?name .
            ?building cr:атакуетТипЦели ?targetUri .
            ?targetUri rdfs:label ?targets .
            OPTIONAL { ?building cr:стоимостьЭликсира ?cost }
            
            FILTER(?targetUri = cr:Наземные || ?targetUri = cr:НаземныеИВоздушные)
        }
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nОборонительные здания: {len(results)}\n")
        for row in results:
            cost = f"{row.cost} эликсира" if row.cost else "неизвестно"
            print(f"  • {row.name} ({cost}) - атакует {row.targets}")
        
        print("\n")
    
    def query_12_archetype_avg_cost(self):
        """
        Вопрос 12: Какая средняя стоимость эликсира у каждого архетипа колоды?
        """
        print("=" * 80)
        print("ВОПРОС 12: Средняя стоимость эликсира по архетипам")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?archetype ?avgCost
        WHERE {
            ?archetypeUri a cr:АрхетипКолоды .
            ?archetypeUri rdfs:label ?archetype .
            OPTIONAL { ?archetypeUri cr:средняяСтоимость ?avgCost }
        }
        ORDER BY ?avgCost
        """
        
        results = self.graph.query(query)
        
        print(f"\nАрхетипы колод:\n")
        for row in results:
            avg = f"{row.avgCost}" if row.avgCost else "не указана"
            print(f"  • {row.archetype}: {avg} эликсира")
        
        print("\n")
    
    def query_13_support_role_cards(self):
        """
        Вопрос 13: Какие карты имеют роль поддержки в колоде?
        """
        print("=" * 80)
        print("ВОПРОС 13: Карты поддержки в колодах")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?name ?cost ?role
        WHERE {
            ?card cr:имеетРольВКолоде ?roleUri .
            ?card rdfs:label ?name .
            ?roleUri rdfs:label ?role .
            OPTIONAL { ?card cr:стоимостьЭликсира ?cost }
            
            FILTER(?roleUri = cr:ТанкПоддержки)
        }
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nКарты с ролью танка поддержки: {len(results)}\n")
        for row in results:
            cost = f"{row.cost} эликсира" if row.cost else "неизвестно"
            print(f"  • {row.name} ({cost}) - {row.role}")
        
        print("\n")
    
    def query_14_building_targets(self):
        """
        Вопрос 14: Какие карты атакуют только здания?
        """
        print("=" * 80)
        print("ВОПРОС 14: Карты, атакующие только здания")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?name ?cost
        WHERE {
            ?card cr:атакуетТипЦели cr:Здания .
            ?card rdfs:label ?name .
            OPTIONAL { ?card cr:стоимостьЭликсира ?cost }
        }
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nКарты, атакующие только здания: {len(results)}\n")
        for row in results:
            cost = f"{row.cost} эликсира" if row.cost else "неизвестно"
            print(f"  • {row.name} ({cost})")
        
        print("\n")
    
    def query_15_versatile_cards(self):
        """
        Вопрос 15: Какие универсальные карты можно использовать и в атаке, и в защите?
        """
        print("=" * 80)
        print("ВОПРОС 15: Универсальные карты (атака и защита)")
        print("=" * 80)
        
        query = """
        PREFIX cr: <http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?name ?cost (GROUP_CONCAT(DISTINCT ?purpose; separator=", ") AS ?purposes)
        WHERE {
            ?card cr:имеетНазначение ?purposeUri .
            ?purposeUri rdfs:label ?purpose .
            ?card rdfs:label ?name .
            OPTIONAL { ?card cr:стоимостьЭликсира ?cost }
            
            # Должны иметь назначение Защита
            FILTER EXISTS { ?card cr:имеетНазначение cr:Защита }
            
            # Также должны иметь атакующие свойства (атакуют цели)
            ?card cr:атакуетТипЦели ?target .
        }
        GROUP BY ?name ?cost
        ORDER BY ?cost ?name
        """
        
        results = self.graph.query(query)
        
        print(f"\nУниверсальные карты: {len(results)}\n")
        for row in results:
            cost = f"{row.cost} эликсира" if row.cost else "неизвестно"
            print(f"  • {row.name} ({cost}) - {row.purposes}")
        
        print("\n")
    
    def run_all_queries(self):
        """Выполнить все компетентностные запросы."""
        print("\n" + "=" * 80)
        print("  СИСТЕМА ПОСТРОЕНИЯ КОЛОД ДЛЯ CLASH ROYALE")
        print("  Компетентностные SPARQL-запросы")
        print("=" * 80)
        print()
        
        self.query_1_hog_cycle_cards()
        self.query_2_common_tactics()
        self.query_3_spawner_buildings()
        self.query_4_balloon_support()
        self.query_5_elixir_collector_archetype()
        self.query_6_knight_replacement_anti_air()
        self.query_7_cycle_cards_low_cost()
        self.query_8_counter_cards()
        self.query_9_synergy_pairs()
        self.query_10_direct_tower_damage()
        self.query_11_defensive_buildings()
        self.query_12_archetype_avg_cost()
        self.query_13_support_role_cards()
        self.query_14_building_targets()
        self.query_15_versatile_cards()


def main():
    """Главная функция."""
    # Путь к онтологии
    ontology_file = "ontology_populated.ttl"
    
    # Если файл еще не создан, используем исходную онтологию
    import os
    if not os.path.exists(ontology_file):
        print(f"Файл {ontology_file} не найден.")
        print("Используем исходную онтологию для демонстрации...\n")
        ontology_file = "ontology.ttl"
    
    # Создаем билдер колод
    builder = DeckBuilder(ontology_file)
    
    # Выполняем все запросы
    builder.run_all_queries()
    
    print("=" * 80)
    print("  ГОТОВО!")
    print("=" * 80)
    print("\nВы можете использовать эти запросы для анализа колод и подбора карт.")
    print()


if __name__ == "__main__":
    main()
